import numpy as np
from scipy.interpolate import BSpline
from scipy.stats import skew, kurtosis
from scipy.fft import dct
from sklearn.model_selection import train_test_split
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import warnings
import optuna
import pywt
import os

warnings.filterwarnings('ignore', message='Level value of.*too high')
warnings.filterwarnings('ignore', message='Precision loss occurred in moment calculation')


class TransformRegistry:
    def __init__(self):
        self._transforms = {
            'raw': lambda d: d,
            'derivative': lambda d: np.gradient(d, axis=-1),
            'second_deriv': lambda d: np.gradient(np.gradient(d, axis=-1), axis=-1),
            'cumsum': lambda d: np.cumsum(d, axis=-1),
            'diff': lambda d: np.diff(d, axis=-1, prepend=d[..., :1]),
            'log1p': lambda d: np.log1p(np.abs(d)),
            'abs': np.abs,
            'sorted': lambda d: np.sort(d, axis=-1),
            'dct': lambda d: dct(d, axis=-1, type=2, norm='ortho'),
            'exp': lambda d: np.exp(np.clip(d, -10, 10)),
            'tanh': np.tanh,
            'sin': np.sin,
            'cos': np.cos,
            'reciprocal': lambda d: 1.0 / (np.abs(d) + 1e-8),
            'fft_power': self._fft_power,
            'autocorr': self._autocorr,
            'wavelet_db4': lambda d: self._wavelet(d, 'db4'),
            'wavelet_sym4': lambda d: self._wavelet(d, 'sym4'),
            'wavelet_coif1': lambda d: self._wavelet(d, 'coif1'),
            'wavelet_haar': lambda d: self._wavelet(d, 'haar'),
        }
    
    def register(self, name, func):
        self._transforms[name] = func
        return self
    
    def get(self, name):
        if callable(name):
            return name
        if name not in self._transforms:
            raise ValueError(f"Transform '{name}' not found. Available: {self.list_all()}")
        return self._transforms[name]
    
    def list_all(self):
        return list(self._transforms.keys())
    
    def apply(self, data, name):
        data = np.ascontiguousarray(data, dtype=np.float32)
        func = self.get(name)
        return func(data).astype(np.float32)
    
    def _wavelet(self, data, wavelet):
        n_samples, n_series, n_time = data.shape
        level = min(3, int(np.log2(n_time)) - 1)
        flat = data.reshape(-1, n_time)
        result = np.empty_like(flat)
        x_out = np.linspace(0, 1, n_time)
        for i in range(flat.shape[0]):
            coeffs = pywt.wavedec(flat[i], wavelet, level=level, mode='periodization')
            cat = np.concatenate(coeffs)
            result[i] = np.interp(x_out, np.linspace(0, 1, len(cat)), cat)
        return result.reshape(n_samples, n_series, n_time)
    
    def _fft_power(self, data):
        n_time = data.shape[-1]
        power = np.abs(np.fft.rfft(data, axis=-1)) ** 2
        n_freq = power.shape[-1]
        flat = power.reshape(-1, n_freq)
        result = np.empty((flat.shape[0], n_time), dtype=np.float32)
        x_in, x_out = np.linspace(0, 1, n_freq), np.linspace(0, 1, n_time)
        for i in range(flat.shape[0]):
            result[i] = np.interp(x_out, x_in, flat[i])
        return result.reshape(data.shape)
    
    def _autocorr(self, data):
        n_samples, n_series, n_time = data.shape
        flat = data.reshape(-1, n_time)
        centered = flat - flat.mean(axis=-1, keepdims=True)
        fft_len = 2 * n_time - 1
        f = np.fft.rfft(centered, n=fft_len, axis=-1)
        acf = np.fft.irfft(f * np.conj(f), n=fft_len, axis=-1)[:, :n_time]
        return (acf / (acf[:, :1] + 1e-8)).reshape(n_samples, n_series, n_time)


class DistanceRegistry:
    def __init__(self):
        self._metrics = {
            'rmse': lambda p, s: np.sqrt(np.mean((s - p) ** 2, axis=1)),
            'mse': lambda p, s: np.mean((s - p) ** 2, axis=1),
            'mae': lambda p, s: np.mean(np.abs(s - p), axis=1),
            'max_abs': lambda p, s: np.max(np.abs(s - p), axis=1),
            'cosine': self._cosine,
            'correlation': self._correlation,
            'euclidean': lambda p, s: np.sqrt(np.sum((s - p) ** 2, axis=1)),
        }
    
    def register(self, name, func):
        self._metrics[name] = func
        return self
    
    def get(self, name):
        if callable(name):
            return name
        if name not in self._metrics:
            raise ValueError(f"Metric '{name}' not found. Available: {self.list_all()}")
        return self._metrics[name]
    
    def list_all(self):
        return list(self._metrics.keys())
    
    def _cosine(self, pattern, segment):
        p_norm = np.linalg.norm(pattern)
        s_norm = np.linalg.norm(segment, axis=1)
        dot = np.sum(segment * pattern, axis=1)
        return 1 - dot / (p_norm * s_norm + 1e-8)
    
    def _correlation(self, pattern, segment):
        p_centered = pattern - np.mean(pattern)
        s_centered = segment - np.mean(segment, axis=1, keepdims=True)
        p_std, s_std = np.std(pattern), np.std(segment, axis=1)
        corr = np.mean(p_centered * s_centered, axis=1) / (p_std * s_std + 1e-8)
        return 1 - corr


TRANSFORMS = TransformRegistry()
DISTANCES = DistanceRegistry()
all_transforms = TRANSFORMS.list_all()


def generate_bspline_pattern(control_points, width):
    n_cp, degree = len(control_points), min(3, len(control_points) - 1)
    knots = np.concatenate([np.zeros(degree + 1), np.linspace(0, 1, n_cp - degree + 1)[1:-1], np.ones(degree + 1)])
    return BSpline(knots, np.asarray(control_points), degree)(np.linspace(0, 1, int(round(width))))


def apply_transformation(data, transform_type):
    return TRANSFORMS.apply(data, transform_type)


def compute_aggregate_stats(transformed_data):
    n_time = transformed_data.shape[2]
    mid = max(1, n_time // 2)
    stats = np.stack([
        np.mean(transformed_data, axis=2),
        np.median(transformed_data, axis=2),
        np.std(transformed_data, axis=2),
        np.min(transformed_data, axis=2),
        np.max(transformed_data, axis=2),
        skew(transformed_data, axis=2, nan_policy='omit'),
        kurtosis(transformed_data, axis=2, nan_policy='omit'),
        np.max(transformed_data, axis=2) - np.min(transformed_data, axis=2),
        np.percentile(transformed_data, 25, axis=2),
        np.percentile(transformed_data, 75, axis=2),
        np.percentile(transformed_data, 75, axis=2) - np.percentile(transformed_data, 25, axis=2),
        np.mean(transformed_data[:, :, :mid], axis=2),
        np.mean(transformed_data[:, :, mid:], axis=2),
        np.std(transformed_data[:, :, :mid], axis=2),
        np.std(transformed_data[:, :, mid:], axis=2),
        np.mean(transformed_data[:, :, mid:], axis=2) - np.mean(transformed_data[:, :, :mid], axis=2),
    ], axis=2)
    return stats.reshape(transformed_data.shape[0], -1)


class EarlyStoppingCallback:
    def __init__(self, patience, direction):
        self.patience, self.direction = patience, direction
        self.best_value, self.best_trial = None, 0
    
    def __call__(self, study, trial):
        val = trial.value
        if val is None:
            return
        is_better = self.best_value is None or (val < self.best_value if self.direction == 'minimize' else val > self.best_value)
        if is_better:
            self.best_value, self.best_trial = val, trial.number
        elif trial.number - self.best_trial >= self.patience:
            study.stop()


class PatternExtractor:
    def __init__(self, model=None, transforms='auto', distance_metric='rmse', n_patterns=15, n_control_points=3, discovery_mode='joint', backward_elimination=True, n_transforms=5, n_trials=300, early_stopping_patience=1000, inner_k_folds=3, max_samples=2000, val_size=0.2, sampler='nsga2', show_progress=True, n_workers=1):
        self.model = model
        self.transforms = transforms
        self.distance_metric = distance_metric
        self.n_patterns = n_patterns
        self.n_control_points = n_control_points
        self.discovery_mode = discovery_mode
        self.backward_elimination = backward_elimination
        self.n_transforms = n_transforms
        self.n_trials = n_trials
        self.early_stopping_patience = early_stopping_patience
        self.inner_k_folds = inner_k_folds
        self.max_samples = max_samples
        self.val_size = val_size
        self.sampler = sampler
        self.show_progress = show_progress
        self.n_workers = n_workers
        self.patterns_ = None
        self.transform_types_ = None
        self.model_ = None
    
    def fit(self, X, y, X_test=None, initial_features=None):
        from .models import LightGBMModelWrapper
        optuna.logging.set_verbosity(optuna.logging.WARNING)
        X = self._prepare_input(X)
        y = np.asarray(y).flatten()
        n_samples, n_series, n_time = X.shape
        metric = self._infer_metric(y)
        y = self._encode_labels(y, metric)
        print(f"\nPatternExtractor: {n_samples} samples, {n_series} channels, {n_time} time points")
        self.transform_types_ = self._select_transforms(X, y, metric)
        print(f"Selected {len(self.transform_types_)} transforms: {self.transform_types_}")
        transformed = np.stack([TRANSFORMS.apply(X, t) for t in self.transform_types_])
        base_feats = initial_features[0] if initial_features else np.empty((n_samples, 0))
        task_type = 'regression' if metric == 'rmse' else 'classification'
        n_classes = len(np.unique(y)) if task_type == 'classification' else 2
        self.model_ = self.model or LightGBMModelWrapper(task_type, n_classes)
        if self.discovery_mode == 'joint':
            patterns, params_list = self._discover_joint(transformed, y, base_feats, n_time, metric)
        else:
            patterns, params_list = self._discover_iterative(transformed, y, base_feats, n_time, metric)
        if self.backward_elimination:
            patterns, params_list = self._backward_eliminate(patterns, params_list, transformed, y, base_feats, metric)
        self.patterns_ = patterns
        print(f"Discovered {len(patterns)} patterns")
        train_feats = self._compute_features(transformed, params_list)
        train_X = np.hstack([base_feats, train_feats]) if base_feats.size else train_feats
        train_idx, val_idx = train_test_split(np.arange(len(y)), test_size=self.val_size, random_state=42)
        self.model_.fit(train_X[train_idx], y[train_idx], train_X[val_idx], y[val_idx])
        test_feats = None
        if X_test is not None:
            X_test = self._prepare_input(X_test)
            transformed_test = np.stack([TRANSFORMS.apply(X_test, t) for t in self.transform_types_])
            test_feats = self._compute_features(transformed_test, params_list)
            if initial_features:
                test_feats = np.hstack([initial_features[1], test_feats])
        return {'patterns': patterns, 'train_features': train_X, 'test_features': test_feats, 'model': self.model_}
    
    def _prepare_input(self, X):
        if isinstance(X, list):
            X = np.stack([x.values if hasattr(x, 'values') else x for x in X], axis=1)
        else:
            X = X.values if hasattr(X, 'values') else X
            if X.ndim == 2:
                X = X[:, np.newaxis, :]
        return X
    
    def _infer_metric(self, y):
        if np.issubdtype(y.dtype, np.floating) and len(np.unique(y)) > 10:
            return 'rmse'
        return 'auc' if len(np.unique(y)) == 2 else 'accuracy'
    
    def _encode_labels(self, y, metric):
        if metric == 'rmse':
            return y
        unique = np.unique(y)
        if len(unique) == 2 and not np.array_equal(unique, [0, 1]):
            return (y == unique[1]).astype(int)
        if not np.array_equal(unique, np.arange(len(unique))):
            return np.array([{v: i for i, v in enumerate(unique)}[v] for v in y])
        return y
    
    def _select_transforms(self, X, y, metric):
        if self.transforms != 'auto':
            return self.transforms if isinstance(self.transforms, list) else [self.transforms]
        from .models import LightGBMModelWrapper
        task_type = 'regression' if metric == 'rmse' else 'classification'
        n_classes = len(np.unique(y)) if task_type == 'classification' else 2
        def eval_transform(t):
            stats = np.nan_to_num(compute_aggregate_stats(TRANSFORMS.apply(X, t)), nan=0, posinf=0, neginf=0)
            return (t, LightGBMModelWrapper(task_type, n_classes, num_threads=1).run_cv(stats, y, 3, metric))
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as ex:
            results = list(ex.map(eval_transform, TRANSFORMS.list_all()))
        results.sort(key=lambda x: x[1], reverse=(metric != 'rmse'))
        return [t for t, _ in results[:self.n_transforms]]
    
    def _discover_joint(self, transformed, y, base_feats, n_time, metric):
        n_samples, n_series = transformed.shape[1], transformed.shape[2]
        max_width = min(50.0, n_time)
        direction = 'minimize' if metric == 'rmse' else 'maximize'
        distance_fn = DISTANCES.get(self.distance_metric)
        search_idx = np.random.choice(n_samples, min(n_samples, self.max_samples), replace=False) if n_samples > self.max_samples else np.arange(n_samples)
        search_stack, search_y = transformed[:, search_idx], y[search_idx]
        search_base = base_feats[search_idx] if base_feats.size else np.empty((len(search_idx), 0))
        def objective(trial):
            params_list = []
            for p in range(self.n_patterns):
                t_idx = trial.suggest_int(f'p{p}_t', 0, len(self.transform_types_) - 1)
                s_idx = trial.suggest_int(f'p{p}_s', 0, n_series - 1) if n_series > 1 else 0
                cps = tuple(trial.suggest_float(f'p{p}_c{i}', 0, 1) for i in range(self.n_control_points))
                center = trial.suggest_int(f'p{p}_pos', 0, n_time - 1)
                width = trial.suggest_float(f'p{p}_w', 2.0, max_width)
                params_list.append((t_idx, s_idx, cps, center, width))
            feats = self._batch_features(search_stack, params_list, distance_fn, n_time)
            X = np.hstack([search_base, feats]) if search_base.size else feats
            return self.model_.run_cv(X, search_y, self.inner_k_folds, metric)
        sampler_obj = optuna.samplers.TPESampler() if self.sampler == 'tpe' else optuna.samplers.NSGAIISampler()
        study = optuna.create_study(direction=direction, sampler=sampler_obj)
        callbacks = [EarlyStoppingCallback(self.early_stopping_patience, direction)] if self.early_stopping_patience else []
        warnings.filterwarnings('ignore', category=optuna.exceptions.ExperimentalWarning)
        study.optimize(objective, n_trials=self.n_trials, show_progress_bar=self.show_progress, n_jobs=self.n_workers, callbacks=callbacks)
        params = study.best_trial.params
        print(f"Best {metric}={study.best_trial.value:.4f} (stopped at trial {len(study.trials)})")
        patterns, params_list = [], []
        for p in range(self.n_patterns):
            t_idx, s_idx = params[f'p{p}_t'], params.get(f'p{p}_s', 0)
            cps = tuple(params[f'p{p}_c{i}'] for i in range(self.n_control_points))
            center, width = params[f'p{p}_pos'], params[f'p{p}_w']
            w = int(round(width))
            start = min(max(0, int(center - w // 2)), n_time - w)
            patterns.append({'pattern': generate_bspline_pattern(cps, width), 'start': start, 'width': width, 'center': center, 'series_idx': s_idx, 'control_points': list(cps), 'transform_type': self.transform_types_[t_idx]})
            params_list.append((t_idx, s_idx, cps, center, width))
        return patterns, params_list
    
    def _discover_iterative(self, transformed, y, base_feats, n_time, metric):
        n_samples, n_series = transformed.shape[1], transformed.shape[2]
        max_width = min(50.0, n_time)
        direction = 'minimize' if metric == 'rmse' else 'maximize'
        distance_fn = DISTANCES.get(self.distance_metric)
        search_idx = np.random.choice(n_samples, min(n_samples, self.max_samples), replace=False) if n_samples > self.max_samples else np.arange(n_samples)
        search_stack, search_y = transformed[:, search_idx], y[search_idx]
        patterns, params_list = [], []
        current_feats = base_feats[search_idx] if base_feats.size else np.empty((len(search_idx), 0))
        for i in range(self.n_patterns):
            def objective(trial):
                t_idx = trial.suggest_int('t', 0, len(self.transform_types_) - 1)
                s_idx = trial.suggest_int('s', 0, n_series - 1) if n_series > 1 else 0
                cps = tuple(trial.suggest_float(f'c{j}', 0, 1) for j in range(self.n_control_points))
                center = trial.suggest_int('pos', 0, n_time - 1)
                width = trial.suggest_float('w', 2.0, max_width)
                new_feat = self._single_feature(search_stack, t_idx, s_idx, cps, center, width, distance_fn, n_time)
                X = np.hstack([current_feats, new_feat.reshape(-1, 1)]) if current_feats.size else new_feat.reshape(-1, 1)
                return self.model_.run_cv(X, search_y, self.inner_k_folds, metric)
            sampler_obj = optuna.samplers.TPESampler() if self.sampler == 'tpe' else optuna.samplers.NSGAIISampler()
            study = optuna.create_study(direction=direction, sampler=sampler_obj)
            n_trials_per = max(50, self.n_trials // self.n_patterns)
            patience = max(100, self.early_stopping_patience // self.n_patterns) if self.early_stopping_patience else None
            callbacks = [EarlyStoppingCallback(patience, direction)] if patience else []
            study.optimize(objective, n_trials=n_trials_per, show_progress_bar=False, callbacks=callbacks)
            p = study.best_trial.params
            t_idx, s_idx = p['t'], p.get('s', 0)
            cps = tuple(p[f'c{j}'] for j in range(self.n_control_points))
            center, width = p['pos'], p['w']
            w = int(round(width))
            start = min(max(0, int(center - w // 2)), n_time - w)
            patterns.append({'pattern': generate_bspline_pattern(cps, width), 'start': start, 'width': width, 'center': center, 'series_idx': s_idx, 'control_points': list(cps), 'transform_type': self.transform_types_[t_idx]})
            params_list.append((t_idx, s_idx, cps, center, width))
            new_feat = self._single_feature(search_stack, t_idx, s_idx, cps, center, width, distance_fn, n_time)
            current_feats = np.hstack([current_feats, new_feat.reshape(-1, 1)]) if current_feats.size else new_feat.reshape(-1, 1)
            print(f"Pattern {i+1}/{self.n_patterns}: {metric}={study.best_trial.value:.4f}")
        return patterns, params_list
    
    def _backward_eliminate(self, patterns, params_list, transformed, y, base_feats, metric):
        all_feats = self._compute_features(transformed, params_list)
        selected = list(range(len(patterns)))
        current_X = np.hstack([base_feats, all_feats]) if base_feats.size else all_feats
        current_score = self.model_.run_cv(current_X, y, self.inner_k_folds, metric)
        while len(selected) > 1:
            worst_idx, worst_score = -1, float('inf') if metric == 'rmse' else -float('inf')
            for i in selected:
                trial_idx = [j for j in selected if j != i]
                feats = all_feats[:, trial_idx]
                X = np.hstack([base_feats, feats]) if base_feats.size else feats
                s = self.model_.run_cv(X, y, self.inner_k_folds, metric)
                if (s < worst_score if metric == 'rmse' else s > worst_score):
                    worst_score, worst_idx = s, i
            tolerance = 0.001
            acceptable = (worst_score <= current_score + tolerance) if metric == 'rmse' else (worst_score >= current_score - tolerance)
            if acceptable and worst_idx != -1:
                selected.remove(worst_idx)
                current_score = worst_score
            else:
                break
        print(f"Reduced from {len(patterns)} to {len(selected)} patterns")
        return [patterns[i] for i in selected], [params_list[i] for i in selected]
    
    def _batch_features(self, stack, params_list, distance_fn, n_time):
        n_samples = stack.shape[1]
        feats = np.empty((n_samples, len(params_list)), dtype=np.float32)
        for i, (t_idx, s_idx, cps, center, width) in enumerate(params_list):
            feats[:, i] = self._single_feature(stack, t_idx, s_idx, cps, center, width, distance_fn, n_time)
        return feats
    
    def _single_feature(self, stack, t_idx, s_idx, cps, center, width, distance_fn, n_time):
        w = int(round(width))
        start = min(max(0, int(center - w // 2)), n_time - w)
        pattern = generate_bspline_pattern(cps, width)
        segment = stack[t_idx, :, s_idx, start:start+w]
        return distance_fn(pattern, segment)
    
    def _compute_features(self, stack, params_list):
        return self._batch_features(stack, params_list, DISTANCES.get(self.distance_metric), stack.shape[3])
    
    def predict(self, X, initial_features=None):
        X = self._prepare_input(X)
        transformed = np.stack([TRANSFORMS.apply(X, t) for t in self.transform_types_])
        params_list = [(self.transform_types_.index(p['transform_type']), p['series_idx'], tuple(p['control_points']), p['center'], p['width']) for p in self.patterns_]
        feats = self._compute_features(transformed, params_list)
        return self.model_.predict(np.hstack([initial_features, feats]) if initial_features is not None else feats)
    
    def predict_proba(self, X, initial_features=None):
        X = self._prepare_input(X)
        transformed = np.stack([TRANSFORMS.apply(X, t) for t in self.transform_types_])
        params_list = [(self.transform_types_.index(p['transform_type']), p['series_idx'], tuple(p['control_points']), p['center'], p['width']) for p in self.patterns_]
        feats = self._compute_features(transformed, params_list)
        return self.model_.predict_proba(np.hstack([initial_features, feats]) if initial_features is not None else feats)


def feature_extraction(input_series_train, y_train, input_series_test=None, initial_features=None, model=None, metric='auc', val_size=0.2, n_trials=300, n_control_points=3, n_patterns=15, n_transforms=5, max_samples=2000, inner_k_folds=3, early_stopping_patience=1000, show_progress=True, n_workers=1, backward_elimination=True, sampler='nsga2', transforms=None, distance_metric='rmse', discovery_mode='joint'):
    extractor = PatternExtractor(model=model, transforms=transforms if transforms else 'auto', distance_metric=distance_metric, n_patterns=n_patterns, n_control_points=n_control_points, discovery_mode=discovery_mode, backward_elimination=backward_elimination, n_transforms=n_transforms, n_trials=n_trials, early_stopping_patience=early_stopping_patience, inner_k_folds=inner_k_folds, max_samples=max_samples, val_size=val_size, sampler=sampler, show_progress=show_progress, n_workers=n_workers)
    return extractor.fit(input_series_train, y_train, input_series_test, initial_features)
