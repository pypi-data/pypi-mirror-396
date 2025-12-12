"""
PatX: Pattern eXtraction for time series and spatial data using B-splines.

Provides interpretable pattern discovery through multi-representation search.
"""

from .core import (
    feature_extraction,
    PatternExtractor,
    TRANSFORMS,
    DISTANCES,
    TransformRegistry,
    DistanceRegistry,
    all_transforms,
    apply_transformation,
    generate_bspline_pattern,
)
from .models import (
    LightGBMModelWrapper,
    BaseModelWrapper,
    SklearnWrapper,
    RandomForestWrapper,
    XGBoostWrapper,
    get_model,
)

__version__ = "0.5.0"
__all__ = [
    "feature_extraction",
    "PatternExtractor",
    "TRANSFORMS",
    "DISTANCES",
    "TransformRegistry",
    "DistanceRegistry",
    "all_transforms",
    "apply_transformation",
    "generate_bspline_pattern",
    "LightGBMModelWrapper",
    "BaseModelWrapper",
    "SklearnWrapper",
    "RandomForestWrapper",
    "XGBoostWrapper",
    "get_model",
]
