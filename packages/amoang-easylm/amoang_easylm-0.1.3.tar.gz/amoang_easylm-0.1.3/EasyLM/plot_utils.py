"""
plot_utils.py - Implementation for PlotHelper
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from math import pi


# HELPERS 

def _get_labels(models):
    """Generate labels from models."""
    return [getattr(m, 'name', f'Model {i+1}') for i, m in enumerate(models)]


def _get_coefs(model):
    """Extract coefficients."""
    if hasattr(model, 'params_'):
        return np.asarray(model.params_).ravel()
    return np.array([])


def _get_metric(model, name):
    """Extract metric value."""
    for attr_name in [name, f'{name}_']:
        if hasattr(model, attr_name):
            attr = getattr(model, attr_name)
            return float(attr() if callable(attr) else attr)
    return np.nan


def _get_stderr(model):
    """Extract standard errors."""
    try:
        if hasattr(model, '_stats'):
            table = model._stats.get_coefficient_table()
            return np.asarray(table['std_err'])
    except:
        pass
    return None


# COEFFICIENT PLOTS

def plot_coefficients_bar(models, labels=None, figsize=(10, 6), **kwargs):
    """Bar chart for coefficients."""
    labels = labels or _get_labels(models)
    
    # Extract and pad coefficients
    all_coefs = [_get_coefs(m) for m in models]
    max_len = max(len(c) for c in all_coefs)
    
    coef_dict = {}
    for label, coefs in zip(labels, all_coefs):
        padded = np.full(max_len, np.nan)
        padded[:len(coefs)] = coefs
        coef_dict[label] = padded
    
    df = pd.DataFrame(coef_dict)
    
    # Plot
    fig, ax = plt.subplots(figsize=figsize)
    x = np.arange(max_len)
    width = 0.8 / len(models)
    
    for i, col in enumerate(df.columns):
        offset = (i - len(models)/2 + 0.5) * width
        ax.bar(x + offset, df[col], width, label=col, alpha=0.8)
    
    ax.set_xlabel('Coefficient', fontweight='bold')
    ax.set_ylabel('Value', fontweight='bold')
    ax.set_title('Coefficient Comparison', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([f'β{i}' for i in range(max_len)])
    ax.axhline(0, color='black', linewidth=0.8)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    return fig


def plot_coefficients_heatmap(models, labels=None, figsize=(10, 6), **kwargs):
    """Heatmap for coefficients."""
    labels = labels or _get_labels(models)
    
    all_coefs = [_get_coefs(m) for m in models]
    max_len = max(len(c) for c in all_coefs)
    
    matrix = []
    for coefs in all_coefs:
        padded = np.full(max_len, np.nan)
        padded[:len(coefs)] = coefs
        matrix.append(padded)
    
    df = pd.DataFrame(matrix, index=labels, 
                     columns=[f'β{i}' for i in range(max_len)])
    
    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(df, annot=True, fmt='.3f', cmap='RdYlGn', center=0, ax=ax,
                linewidths=0.5, cbar_kws={'label': 'Value'})
    ax.set_title('Coefficient Heatmap', fontweight='bold')
    plt.tight_layout()
    
    return fig


def plot_coefficient_ci(models, labels=None, figsize=(10, 6), **kwargs):
    """Coefficients with 95% confidence intervals."""
    labels = labels or _get_labels(models)
    
    all_coefs = [_get_coefs(m) for m in models]
    all_stderr = [_get_stderr(m) for m in models]
    max_len = max(len(c) for c in all_coefs)
    
    fig, ax = plt.subplots(figsize=figsize)
    x = np.arange(max_len)
    width = 0.8 / len(models)
    
    for i, (label, coefs, stderr) in enumerate(zip(labels, all_coefs, all_stderr)):
        padded = np.full(max_len, np.nan)
        padded[:len(coefs)] = coefs
        offset = (i - len(models)/2 + 0.5) * width
        
        if stderr is not None:
            padded_se = np.full(max_len, 0)
            padded_se[:len(stderr)] = stderr
            ax.errorbar(x + offset, padded, yerr=padded_se*1.96,
                       fmt='o', label=label, capsize=5)
        else:
            ax.scatter(x + offset, padded, label=label, s=100)
    
    ax.set_xlabel('Coefficient', fontweight='bold')
    ax.set_ylabel('Value', fontweight='bold')
    ax.set_title('Coefficients with 95% CI', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([f'β{i}' for i in range(max_len)])
    ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    return fig


# METRIC PLOTS 

def plot_metrics_bar(models, metrics, labels=None, figsize=(10, 6), **kwargs):
    """Bar chart for metrics."""
    labels = labels or _get_labels(models)
    
    data = {m: [_get_metric(model, m) for model in models] for m in metrics}
    df = pd.DataFrame(data, index=labels)
    
    fig, ax = plt.subplots(figsize=figsize)
    x = np.arange(len(metrics))
    width = 0.8 / len(models)
    
    for i, (label, row) in enumerate(df.iterrows()):
        offset = (i - len(models)/2 + 0.5) * width
        ax.bar(x + offset, row.values, width, label=label, alpha=0.8)
    
    ax.set_xlabel('Metrics', fontweight='bold')
    ax.set_ylabel('Value', fontweight='bold')
    ax.set_title('Model Metrics', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([m.upper().replace('_', ' ') for m in metrics])
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    return fig


def plot_metrics_radar(models, metrics, labels=None, figsize=(8, 8), **kwargs):
    """Radar/spider chart for metrics."""
    labels = labels or _get_labels(models)
    
    # Normalize metrics to 0-1
    data = {}
    for m in metrics:
        values = [_get_metric(model, m) for model in models]
        if not all(np.isnan(values)):
            vmin, vmax = np.nanmin(values), np.nanmax(values)
            if vmax > vmin:
                values = [(v - vmin)/(vmax - vmin) for v in values]
        data[m] = values
    
    df = pd.DataFrame(data, index=labels)
    
    angles = np.linspace(0, 2*pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(projection='polar'))
    
    for i, (label, row) in enumerate(df.iterrows()):
        values = row.values.tolist() + row.values.tolist()[:1]
        ax.plot(angles, values, 'o-', linewidth=2, label=label)
        ax.fill(angles, values, alpha=0.15)
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([m.upper().replace('_', ' ') for m in metrics])
    ax.set_ylim(0, 1)
    ax.set_title('Model Performance Radar', fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1))
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    
    return fig


def plot_metrics_heatmap(models, metrics, labels=None, figsize=(10, 6), **kwargs):
    """Heatmap for metrics."""
    labels = labels or _get_labels(models)
    
    data = {m: [_get_metric(model, m) for model in models] for m in metrics}
    df = pd.DataFrame(data, index=labels)
    
    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(df, annot=True, fmt='.4f', cmap='RdYlGn', ax=ax,
                linewidths=0.5, cbar_kws={'label': 'Value'})
    ax.set_title('Metrics Heatmap', fontweight='bold')
    ax.set_xticklabels([m.upper().replace('_', ' ') for m in metrics], 
                       rotation=45, ha='right')
    plt.tight_layout()
    
    return fig


# DASHBOARD 

def plot_dashboard(models, labels=None, figsize=(14, 10)):
    """2x2 comparison dashboard."""
    labels = labels or _get_labels(models)
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    
    # 1. Coefficient bar (reuse code)
    ax = axes[0, 0]
    all_coefs = [_get_coefs(m) for m in models]
    max_len = max(len(c) for c in all_coefs)
    coef_dict = {}
    for label, coefs in zip(labels, all_coefs):
        padded = np.full(max_len, np.nan)
        padded[:len(coefs)] = coefs
        coef_dict[label] = padded
    df = pd.DataFrame(coef_dict)
    x = np.arange(max_len)
    width = 0.8 / len(models)
    for i, col in enumerate(df.columns):
        offset = (i - len(models)/2 + 0.5) * width
        ax.bar(x + offset, df[col], width, label=col, alpha=0.8)
    ax.set_xlabel('Coefficient', fontweight='bold', fontsize=10)
    ax.set_ylabel('Value', fontweight='bold', fontsize=10)
    ax.set_title('Coefficients', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([f'β{i}' for i in range(max_len)], fontsize=8)
    ax.axhline(0, color='black', linewidth=0.8)
    ax.legend(fontsize=8)
    ax.grid(axis='y', alpha=0.3)
    
    # 2. Coefficient heatmap
    ax = axes[0, 1]
    matrix = []
    for coefs in all_coefs:
        padded = np.full(max_len, np.nan)
        padded[:len(coefs)] = coefs
        matrix.append(padded)
    df = pd.DataFrame(matrix, index=labels, columns=[f'β{i}' for i in range(max_len)])
    sns.heatmap(df, annot=True, fmt='.2f', cmap='RdYlGn', center=0, ax=ax,
                linewidths=0.5, cbar_kws={'label': 'Value'})
    ax.set_title('Coefficient Heatmap', fontweight='bold')
    
    # 3. Metric bar
    ax = axes[1, 0]
    metrics = ['r_squared', 'aic', 'bic']
    data = {m: [_get_metric(model, m) for model in models] for m in metrics}
    df = pd.DataFrame(data, index=labels)
    x = np.arange(len(metrics))
    width = 0.8 / len(models)
    for i, (label, row) in enumerate(df.iterrows()):
        offset = (i - len(models)/2 + 0.5) * width
        ax.bar(x + offset, row.values, width, label=label, alpha=0.8)
    ax.set_xlabel('Metrics', fontweight='bold', fontsize=10)
    ax.set_ylabel('Value', fontweight='bold', fontsize=10)
    ax.set_title('Metrics', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(['R²', 'AIC', 'BIC'], fontsize=9)
    ax.legend(fontsize=8)
    ax.grid(axis='y', alpha=0.3)
    
    # 4. Metric table
    ax = axes[1, 1]
    ax.axis('off')
    table_data = [[f"{_get_metric(m, metric):.4f}" for metric in metrics]
                  for m in models]
    table = ax.table(cellText=table_data, rowLabels=labels,
                    colLabels=['R²', 'AIC', 'BIC'],
                    cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    ax.set_title('Metric Summary', fontweight='bold', pad=20)
    
    fig.suptitle('Model Comparison Dashboard', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    return fig