"""
PlotHelper: interface for model comparison plots.
Implementation in plot_utils.py
"""

from .plot_utils import (
    plot_coefficients_bar,
    plot_coefficients_heatmap,
    plot_coefficient_ci,
    plot_metrics_bar,
    plot_metrics_radar,
    plot_metrics_heatmap,
    plot_dashboard
)


class PlotHelper:
    """
    model comparison (coefficients & metrics only).
    """
    
    @staticmethod
    def coef_plot(*models, style='bar', **kwargs):
        """Compare coefficients (bar or heatmap)."""
        if style == 'bar':
            return plot_coefficients_bar(models, **kwargs)
        elif style == 'heatmap':
            return plot_coefficients_heatmap(models, **kwargs)
        else:
            raise ValueError("style must be 'bar' or 'heatmap'")
    
    @staticmethod
    def coef_ci_plot(*models, **kwargs):
        """Coefficients with confidence intervals."""
        return plot_coefficient_ci(models, **kwargs)
    
    @staticmethod
    def metric_plot(*models, style='bar', metrics=None, **kwargs):
        """Compare metrics (bar, radar, or heatmap)."""
        if metrics is None:
            metrics = ['r_squared', 'aic', 'bic']
        
        if style == 'bar':
            return plot_metrics_bar(models, metrics, **kwargs)
        elif style == 'radar':
            return plot_metrics_radar(models, metrics, **kwargs)
        elif style == 'heatmap':
            return plot_metrics_heatmap(models, metrics, **kwargs)
        else:
            raise ValueError("style must be 'bar', 'radar', or 'heatmap'")
    
    @staticmethod
    def compare(*models, **kwargs):
        """Complete 2x2 dashboard."""
        return plot_dashboard(models, **kwargs)