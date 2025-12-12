# PatX - Pattern eXtraction for Time Series and Spatial Data

[![PyPI version](https://badge.fury.io/py/patx.svg)](https://badge.fury.io/py/patx)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

PatX bridges the gap between automatic pattern learning of CNNs and interpretability requirements of biomedical applications. It discovers explicit, human-readable B-spline templates that can be visualized and validated.

## Installation

```bash
pip install patx
```

## Quick Start

```python
import numpy as np
from patx import feature_extraction

# Data shape: (n_samples, n_channels, n_timepoints) or list of DataFrames
X_train = np.random.randn(100, 3, 50)
y_train = np.random.randint(0, 2, 100)

result = feature_extraction(X_train, y_train, X_test)
predictions = result['model'].predict(result['test_features'])
```

## Custom Transforms

Register your own signal transformations:

```python
from patx import TRANSFORMS, PatternExtractor

def my_hilbert(data):
    from scipy.signal import hilbert
    return np.abs(hilbert(data, axis=-1))

TRANSFORMS.register('hilbert', my_hilbert)

extractor = PatternExtractor(transforms=['raw', 'derivative', 'hilbert'])
```

**Built-in transforms:** `raw`, `derivative`, `second_deriv`, `cumsum`, `diff`, `log1p`, `abs`, `sorted`, `dct`, `exp`, `tanh`, `sin`, `cos`, `reciprocal`, `fft_power`, `autocorr`, `wavelet_db4`, `wavelet_sym4`, `wavelet_coif1`, `wavelet_haar`

## Custom Distance Metrics

```python
from patx import DISTANCES, PatternExtractor

def dtw_distance(pattern, segments):
    from tslearn.metrics import dtw
    return np.array([dtw(pattern, seg) for seg in segments])

DISTANCES.register('dtw', dtw_distance)

extractor = PatternExtractor(distance_metric='dtw')
```

**Built-in metrics:** `rmse`, `mse`, `mae`, `max_abs`, `cosine`, `correlation`, `euclidean`

## Custom ML Models

```python
from patx import PatternExtractor, XGBoostWrapper, RandomForestWrapper, SklearnWrapper
from sklearn.svm import SVC

# Built-in wrappers
extractor = PatternExtractor(model=XGBoostWrapper(task_type='classification'))

# Wrap any sklearn model
extractor = PatternExtractor(model=SklearnWrapper(SVC(probability=True)))
```

## Discovery Modes

### Joint Mode (default)
Optimizes all patterns simultaneously:
```python
extractor = PatternExtractor(discovery_mode='joint', n_patterns=15)
```

### Iterative Mode
Discovers patterns one at a time, greedily:
```python
extractor = PatternExtractor(discovery_mode='iterative', n_patterns=10)
```

## Full API

```python
PatternExtractor(
    model=None,                      # LightGBM, XGBoost, RF, or sklearn estimator
    transforms='auto',               # 'auto' or list of transform names
    distance_metric='rmse',          # metric name or callable
    n_patterns=15,                   # patterns to discover
    n_control_points=3,              # B-spline control points
    discovery_mode='joint',          # 'joint' or 'iterative'
    backward_elimination=True,       # remove redundant patterns
    n_transforms=5,                  # transforms to auto-select
    n_trials=300,                    # optimization trials
    early_stopping_patience=1000,    # stop if no improvement
    sampler='nsga2',                 # 'nsga2' or 'tpe'
    inner_k_folds=3,                 # CV folds for evaluation
    max_samples=2000,                # subsample for faster search
    val_size=0.2,                    # validation split
)
```

## Legacy API

```python
from patx import feature_extraction

result = feature_extraction(
    input_series_train=X_train,
    y_train=y_train,
    input_series_test=X_test,
    metric='auc',                    # 'auc', 'accuracy', or 'rmse'
    n_patterns=15,
    backward_elimination=True,
    distance_metric='rmse',
    discovery_mode='joint',
)
```

## Output

```python
result = extractor.fit(X_train, y_train, X_test)

result['patterns']        # List of pattern dicts
result['train_features']  # Feature matrix for training
result['test_features']   # Feature matrix for test
result['model']           # Trained model
```

## Citation

```bibtex
@software{patx,
  title={PatX: Pattern eXtraction for Time Series and Spatial Data},
  author={Wolber, J.},
  year={2025},
  url={https://github.com/Prgrmmrjns/patX}
}
```
