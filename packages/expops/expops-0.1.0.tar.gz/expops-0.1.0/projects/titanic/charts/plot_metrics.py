from typing import Dict, Any

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import threading

from mlops.reporting import chart, ChartContext

@chart()
def nn_a_loss(probe_paths: Dict[str, str], ctx: ChartContext) -> None:
    """
    Dynamic chart for NN branch A training loss over epochs.
    Expects a probe path mapping, e.g., {"nn_a": <probe_path>}.
    """

    latest_metrics: Dict[str, Any] = {}
    render_event = threading.Event()

    def on_snapshot(probe_key, doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            if doc.exists:
                latest_metrics[probe_key] = doc.to_dict() or {}
        render_event.set()

    def to_series(data):
        if isinstance(data, dict):
            items = sorted(data.items(), key=lambda x: int(x[0]) if str(x[0]).isdigit() else 0)
            return [float(v) for _, v in items]
        if isinstance(data, list):
            return [float(v) for v in data]
        return []

    def render_chart():
        if not latest_metrics:
            return
        plt.figure(figsize=(9, 4))
        for idx, (probe_key, _) in enumerate(probe_paths.items()):
            metrics = latest_metrics.get(probe_key, {})
            loss_series = to_series(metrics.get('train_loss', {}))
            if loss_series:
                xs = list(range(1, len(loss_series) + 1))
                plt.plot(xs, loss_series, marker='o', label=probe_key.replace('_', ' ').title())
        plt.title('NN A - Training Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        ctx.savefig('series_train_loss.png', dpi=150)
        plt.close()

    listeners = []
    try:
        for probe_key, probe_path in probe_paths.items():
            metrics_ref = ctx.get_probe_metrics_ref_by_path(probe_path)
            if metrics_ref:
                callback = lambda ds, ch, rt, pk=probe_key: on_snapshot(pk, ds, ch, rt)
                listeners.append(metrics_ref.on_snapshot(callback))

        render_chart()
        while True:
            if render_event.wait(timeout=60.0):
                render_event.clear()
                render_chart()
    finally:
        for listener in listeners:
            try:
                listener.unsubscribe()
            except:
                pass


@chart()
def nn_b_loss(probe_paths: Dict[str, str], ctx: ChartContext) -> None:
    """
    Dynamic chart for NN branch B training loss over epochs.
    Expects a single probe path mapping, e.g., {"nn_b": <probe_path>}.
    """

    latest_metrics: Dict[str, Any] = {}
    render_event = threading.Event()

    def on_snapshot(probe_key, doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            if doc.exists:
                latest_metrics[probe_key] = doc.to_dict() or {}
        render_event.set()

    def to_series(data):
        if isinstance(data, dict):
            items = sorted(data.items(), key=lambda x: int(x[0]) if str(x[0]).isdigit() else 0)
            return [float(v) for _, v in items]
        if isinstance(data, list):
            return [float(v) for v in data]
        return []

    def render_chart():
        if not latest_metrics:
            return
        plt.figure(figsize=(9, 4))
        for idx, (probe_key, _) in enumerate(probe_paths.items()):
            metrics = latest_metrics.get(probe_key, {})
            loss_series = to_series(metrics.get('train_loss', {}))
            if loss_series:
                xs = list(range(1, len(loss_series) + 1))
                plt.plot(xs, loss_series, marker='o', label=probe_key.replace('_', ' ').title())
        plt.title('NN B - Training Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        ctx.savefig('series_train_loss.png', dpi=150)
        plt.close()

    listeners = []
    try:
        for probe_key, probe_path in probe_paths.items():
            metrics_ref = ctx.get_probe_metrics_ref_by_path(probe_path)
            if metrics_ref:
                callback = lambda ds, ch, rt, pk=probe_key: on_snapshot(pk, ds, ch, rt)
                listeners.append(metrics_ref.on_snapshot(callback))

        render_chart()
        while True:
            if render_event.wait(timeout=60.0):
                render_event.clear()
                render_chart()
    finally:
        for listener in listeners:
            try:
                listener.unsubscribe()
            except:
                pass


@chart()
def test_metrics_comparison(metrics: Dict[str, Any], ctx: ChartContext) -> None:
    """
    Static chart comparing test accuracy and precision across NN A, NN B, and Linear.
    Expects metrics structure:
      {"nn_a": {"test_accuracy": {"step": "val", ...}, "test_precision": {"step": "val", ...}}, ...}
    Values may be numbers or dicts of step->value.
    """

    def get_value(data):
        if isinstance(data, dict) and data:
            items = sorted(data.items(), key=lambda x: int(x[0]) if str(x[0]).isdigit() else 0)
            return float(items[-1][1]) if items else None
        if isinstance(data, (int, float)):
            return float(data)
        return None

    groups = {
        'NN A': metrics.get('nn_a', {}),
        'NN B': metrics.get('nn_b', {}),
        'Linear': metrics.get('linear', {}),
    }

    accs = []
    precs = []
    labels = []
    for label, m in groups.items():
        acc = get_value(m.get('test_accuracy'))
        prec = get_value(m.get('test_precision'))
        if acc is None and prec is None:
            continue
        labels.append(label)
        accs.append(acc if acc is not None else 0.0)
        precs.append(prec if prec is not None else 0.0)

    if not labels:
        return

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 4))
    rects1 = ax.bar(x - width/2, accs, width, label='Accuracy', color='steelblue')
    rects2 = ax.bar(x + width/2, precs, width, label='Precision', color='coral')

    ax.set_ylabel('Score')
    ax.set_title('Test Metrics Comparison')
    ax.set_xticks(x, labels)
    ax.legend()
    ax.grid(True, axis='y', alpha=0.3)

    for rect in rects1 + tuple(rects2):
        height = rect.get_height()
        ax.annotate(f'{height:.3f}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    ctx.savefig('test_metrics_comparison.png', dpi=150)
    plt.close()