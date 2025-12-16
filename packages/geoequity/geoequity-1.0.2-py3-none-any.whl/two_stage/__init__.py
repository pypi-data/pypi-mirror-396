"""
TwoStageModel: Two-Stage Spatial Accuracy Prediction
=====================================================

Stage 1: Monotonic GAM on density features (density, sufficiency)
Stage 2: SVM on spatial features to predict residuals

Example:
    >>> from geoequity import TwoStageModel
    >>> model = TwoStageModel(resolution=[30, 30])
    >>> model.fit(df, model_name='linear', bins_intervals=bins)
    >>> model.diagnose(save_dir='output/')
    >>> accuracy = model.predict(lon, lat, density, sufficiency)
"""

from .model import TwoStageModel, find_bins_intervals
from .visualization import plot_predicted_accuracy_map, predict_at_locations

__all__ = ['TwoStageModel', 'find_bins_intervals', 'plot_predicted_accuracy_map', 'predict_at_locations']

