import numpy as np
from abc import ABC, abstractmethod
from sklearn.model_selection import StratifiedKFold, KFold, train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score, mean_squared_error
from sklearn.preprocessing import label_binarize

class BaseModelWrapper(ABC):
    @abstractmethod
    def fit(self, X_train, y_train, X_val=None, y_val=None): pass
    @abstractmethod
    def predict(self, X): pass
    @abstractmethod
    def predict_proba(self, X): pass
    @abstractmethod
    def clone(self): pass
    
    def run_cv(self, X, y, folds, metric):
        if isinstance(folds, int) and folds == 1:
            X_tr, X_val, y_tr, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
            model = self.clone()
            model.fit(X_tr, y_tr, X_val, y_val)
            return self._compute_metric(model, X_val, y_val, metric)
        cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=42) if metric != 'rmse' else KFold(n_splits=folds, shuffle=True, random_state=42)
        scores = []
        for train_idx, val_idx in cv.split(X, y):
            model = self.clone()
            model.fit(X[train_idx], y[train_idx], X[val_idx], y[val_idx])
            scores.append(self._compute_metric(model, X[val_idx], y[val_idx], metric))
        return np.mean(scores)
    
    def _compute_metric(self, model, X, y, metric):
        if metric == 'rmse':
            return np.sqrt(mean_squared_error(y, model.predict(X)))
        elif metric == 'auc':
            proba = model.predict_proba(X)
            n_classes = len(np.unique(y))
            if n_classes > 2:
                y_bin = label_binarize(y, classes=np.arange(n_classes))
                return roc_auc_score(y_bin, proba, multi_class='ovr', average='macro')
            return roc_auc_score(y, proba if proba.ndim == 1 else proba[:, 1]) if len(np.unique(y)) > 1 else 0.5
        elif metric == 'accuracy':
            return accuracy_score(y, model.predict(X))
        return 0.0


class LightGBMModelWrapper(BaseModelWrapper):
    def __init__(self, task_type='classification', n_classes=None, num_threads=1, **kwargs):
        self.task_type = task_type
        self.n_classes = n_classes
        self.params = {
            'boosting_type': 'goss', 'verbosity': -1, 'max_depth': 3,
            'n_estimators': 100, 'learning_rate': 0.2, 'force_row_wise': True,
            'num_threads': num_threads
        }
        if task_type == 'classification':
            self.params['objective'] = 'multiclass' if n_classes and n_classes > 2 else 'binary'
            if n_classes and n_classes > 2:
                self.params['num_class'] = n_classes
        else:
            self.params['objective'] = 'regression'
        self.params.update({k: v for k, v in kwargs.items() if k not in ['task_type', 'n_classes', 'num_threads']})
        self.model = None
    
    def fit(self, X_train, y_train, X_val=None, y_val=None):
        import lightgbm as lgb
        dtrain = lgb.Dataset(X_train, label=y_train)
        params = self.params.copy()
        num_boost = params.pop('n_estimators')
        valid_sets = [lgb.Dataset(X_val, label=y_val, reference=dtrain)] if X_val is not None else []
        callbacks = [lgb.early_stopping(10, verbose=False)] if X_val is not None else []
        self.model = lgb.train(params, dtrain, num_boost_round=num_boost, valid_sets=valid_sets, callbacks=callbacks)
        return self
    
    def predict(self, X):
        preds = self.model.predict(X)
        if self.task_type == 'classification':
            return np.argmax(preds, axis=1) if self.n_classes and self.n_classes > 2 else (preds > 0.5).astype(int)
        return preds
    
    def predict_proba(self, X):
        return self.model.predict(X)
    
    def clone(self):
        return LightGBMModelWrapper(self.task_type, self.n_classes, **self.params)


class SklearnWrapper(BaseModelWrapper):
    def __init__(self, estimator, task_type='classification'):
        self.estimator = estimator
        self.task_type = task_type
        self.model = None
    
    def fit(self, X_train, y_train, X_val=None, y_val=None):
        from sklearn.base import clone
        self.model = clone(self.estimator)
        self.model.fit(X_train, y_train)
        return self
    
    def predict(self, X):
        return self.model.predict(X)
    
    def predict_proba(self, X):
        if hasattr(self.model, 'predict_proba'):
            proba = self.model.predict_proba(X)
            return proba[:, 1] if proba.shape[1] == 2 else proba
        return self.model.predict(X)
    
    def clone(self):
        from sklearn.base import clone
        return SklearnWrapper(clone(self.estimator), self.task_type)


class RandomForestWrapper(SklearnWrapper):
    def __init__(self, task_type='classification', n_estimators=100, max_depth=5, **kwargs):
        if task_type == 'classification':
            from sklearn.ensemble import RandomForestClassifier
            estimator = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, n_jobs=-1, **kwargs)
        else:
            from sklearn.ensemble import RandomForestRegressor
            estimator = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth, n_jobs=-1, **kwargs)
        super().__init__(estimator, task_type)


class XGBoostWrapper(BaseModelWrapper):
    def __init__(self, task_type='classification', n_classes=None, **kwargs):
        self.task_type = task_type
        self.n_classes = n_classes
        self.params = {'max_depth': 3, 'n_estimators': 100, 'learning_rate': 0.2, 'verbosity': 0}
        if task_type == 'classification':
            self.params['objective'] = 'multi:softprob' if n_classes and n_classes > 2 else 'binary:logistic'
            self.params['eval_metric'] = 'mlogloss' if n_classes and n_classes > 2 else 'logloss'
        else:
            self.params['objective'] = 'reg:squarederror'
        self.params.update(kwargs)
        self.model = None
    
    def fit(self, X_train, y_train, X_val=None, y_val=None):
        import xgboost as xgb
        params = self.params.copy()
        n_est = params.pop('n_estimators')
        self.model = xgb.XGBClassifier(**params, n_estimators=n_est) if self.task_type == 'classification' else xgb.XGBRegressor(**params, n_estimators=n_est)
        eval_set = [(X_val, y_val)] if X_val is not None else None
        self.model.fit(X_train, y_train, eval_set=eval_set, verbose=False)
        return self
    
    def predict(self, X):
        return self.model.predict(X)
    
    def predict_proba(self, X):
        if hasattr(self.model, 'predict_proba'):
            proba = self.model.predict_proba(X)
            return proba[:, 1] if proba.shape[1] == 2 else proba
        return self.model.predict(X)
    
    def clone(self):
        return XGBoostWrapper(self.task_type, self.n_classes, **self.params)


def get_model(name='lightgbm', task_type='classification', n_classes=None, **kwargs):
    models = {
        'lightgbm': lambda: LightGBMModelWrapper(task_type, n_classes, **kwargs),
        'xgboost': lambda: XGBoostWrapper(task_type, n_classes, **kwargs),
        'random_forest': lambda: RandomForestWrapper(task_type, **kwargs),
    }
    if name in models:
        return models[name]()
    raise ValueError(f"Unknown model: {name}. Available: {list(models.keys())}")
