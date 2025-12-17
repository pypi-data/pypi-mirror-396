from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

import logging
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, f1_score

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from mlops.core import (
    step, process, SerializableData, log_metric
)

logger = logging.getLogger(__name__)

def _csv_path() -> Path:
    #return Path(__file__).parent.parent / "data" / "England CSV.csv"
    return Path("/home/e/e0958526/mlops-platform/projects/premier-league/data/England CSV.csv")

def _get_result_column_name(df: pd.DataFrame) -> str:
    if 'FT Result' in df.columns:
        return 'FT Result'
    if 'FTR' in df.columns:
        return 'FTR'
    raise ValueError("Missing required result column: expected 'FT Result' or 'FTR'")


def _derive_outcome_labels(df: pd.DataFrame) -> np.ndarray:
    result_col = _get_result_column_name(df)
    mapping = {'H': 0, 'D': 1, 'A': 2}
    y = df[result_col].astype(str).map(mapping)
    if y.isnull().any():
        bad = df.loc[y.isnull(), result_col].unique().tolist()
        raise ValueError(f"Unexpected values in {result_col}: {bad}")
    return y.astype(int).to_numpy()


def _get_cat_num_cols(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    cat_cols = [c for c in ['Season', 'HomeTeam', 'AwayTeam', 'Referee', 'League'] if c in df.columns]
    num_cols = [
        c for c in [
            'HTH Goals', 'HTA Goals', 'H Shots', 'A Shots', 'H SOT', 'A SOT',
            'H Fouls', 'A Fouls', 'H Corners', 'A Corners', 'H Yellow', 'A Yellow',
            'H Red', 'A Red', 'Display_Order', 'DayOfWeek', 'Month'
        ] if c in df.columns
    ]
    return cat_cols, num_cols


def _build_features_dataframe(df: pd.DataFrame, cat_cols: list[str], num_cols: list[str]) -> pd.DataFrame:
    X_df = pd.DataFrame(index=df.index)
    # Numeric
    for c in num_cols:
        s = pd.to_numeric(df[c], errors='coerce')
        if s.isnull().any():
            med = s.median()
            s = s.fillna(med if not np.isnan(med) else 0)
        X_df[c] = s.astype(float)
    for c in cat_cols:
        X_df[c] = df[c].astype(str)
    for drop_c in ['FT Result', 'FTR', 'HT Result', 'Date']:
        if drop_c in X_df.columns:
            X_df = X_df.drop(columns=[drop_c])
    return X_df


@process()
def define_feature_engineering_generic_process(data, hyperparameters):
    """Load CSV, parse dates, derive labels (H/D/A), stratified split indices, and log analysis metrics."""

    @step()
    def load_csv():
        path = _csv_path()
        if not path.exists():
            raise FileNotFoundError(f"Premier League CSV not found at {path}")
        df = pd.read_csv(path)
        try:
            logger.info(f"[feature_engineering_generic.load_csv] Loaded df shape: {df.shape}")
        except Exception:
            pass
        return {'df': df.to_dict(orient='list')}

    @step()
    def derive_labels_and_indices(raw: SerializableData, hyperparameters: Dict[str, Any] | None = None):
        df = pd.DataFrame(raw['df'])
        # Parse date-based features
        if 'Date' in df.columns:
            dt = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
            df['DayOfWeek'] = dt.dt.weekday.fillna(0).astype(int)
            df['Month'] = dt.dt.month.fillna(1).astype(int)
        else:
            df['DayOfWeek'] = 0
            df['Month'] = 1

        y = _derive_outcome_labels(df)

        # Stratified split indices
        test_size = float((hyperparameters or {}).get('test_size', 0.2))
        idx = np.arange(len(df))
        idx_train, idx_test = train_test_split(idx, test_size=test_size, shuffle=True, stratify=y)

        # Goals histograms for static charts
        hist_home = {}
        hist_away = {}
        if 'FTH Goals' in df.columns and 'FTA Goals' in df.columns:
            goals_home = pd.to_numeric(df['FTH Goals'], errors='coerce').fillna(0).astype(int)
            goals_away = pd.to_numeric(df['FTA Goals'], errors='coerce').fillna(0).astype(int)
            hist_home = goals_home.value_counts().sort_index().astype(int).to_dict()
            hist_away = goals_away.value_counts().sort_index().astype(int).to_dict()
            log_metric('goals_hist_home', hist_home)
            log_metric('goals_hist_away', hist_away)

        return {
            'df': df.to_dict(orient='list'),
            'labels': y.astype(int).tolist(),
            'train_idx': idx_train.astype(int).tolist(),
            'test_idx': idx_test.astype(int).tolist(),
            'n_train': int(idx_train.shape[0]),
            'n_test': int(idx_test.shape[0])
        }

    @step()
    def feature_analysis(basic: SerializableData, hyperparameters: Dict[str, Any] | None = None):
        df = pd.DataFrame(basic['df'])
        if 'DayOfWeek' not in df.columns or 'Month' not in df.columns:
            if 'Date' in df.columns:
                dt = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
                df['DayOfWeek'] = dt.dt.weekday.fillna(0).astype(int)
                df['Month'] = dt.dt.month.fillna(1).astype(int)
            else:
                df['DayOfWeek'] = 0
                df['Month'] = 1

        cat_cols, num_cols = _get_cat_num_cols(df)
        X_df = _build_features_dataframe(df, cat_cols, num_cols)

        encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
        preprocessor = ColumnTransformer(
            transformers=[
                ('cat', encoder, cat_cols),
                ('num', StandardScaler(), num_cols)
            ],
            remainder='drop'
        )

        X_all = preprocessor.fit_transform(X_df)
        pca_components = int((hyperparameters or {}).get('pca_components', 16))
        n_components = min(pca_components, X_all.shape[1]) if X_all.shape[1] > 0 else 0
        if n_components > 0:
            pca = PCA(n_components=n_components, random_state=int((hyperparameters or {}).get('random_seed', 42)))
            _ = pca.fit_transform(X_all)
            evr = pca.explained_variance_ratio_.tolist()
            cum = np.cumsum(pca.explained_variance_ratio_).tolist()
        else:
            evr = []
            cum = []

        log_metric('pca_explained_variance_ratio', evr)
        log_metric('pca_cumulative_variance', cum)
        return {}

    raw = load_csv()
    basic = derive_labels_and_indices(raw=raw, hyperparameters=hyperparameters)
    _ = feature_analysis(basic=basic, hyperparameters=hyperparameters)
    return basic


@process()
def define_preprocess_linear_nn_process(data):
    """Preprocess for Linear/NN: OHE categorical + StandardScaler numeric."""
    src = data.get('feature_engineering_generic', {})
    df = pd.DataFrame(src['df'])
    y = np.asarray(src['labels'], dtype=int)
    idx_train = np.asarray(src['train_idx'], dtype=int)
    idx_test = np.asarray(src['test_idx'], dtype=int)

    # Date-derived columns already present from FE; if not, add defaults
    if 'DayOfWeek' not in df.columns or 'Month' not in df.columns:
        if 'Date' in df.columns:
            dt = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
            df['DayOfWeek'] = dt.dt.weekday.fillna(0).astype(int)
            df['Month'] = dt.dt.month.fillna(1).astype(int)
        else:
            df['DayOfWeek'] = 0
            df['Month'] = 1

    cat_cols, num_cols = _get_cat_num_cols(df)
    X_df = _build_features_dataframe(df, cat_cols, num_cols)

    encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', encoder, cat_cols),
            ('num', StandardScaler(), num_cols)
        ],
        remainder='drop'
    )

    X_train = preprocessor.fit_transform(X_df.iloc[idx_train])
    X_test = preprocessor.transform(X_df.iloc[idx_test])
    y_train = y[idx_train]
    y_test = y[idx_test]

    return {
        'X_train': X_train.astype(float).tolist(),
        'X_test': X_test.astype(float).tolist(),
        'y_train': y_train.astype(int).tolist(),
        'y_test': y_test.astype(int).tolist(),
        'row_indices_train': idx_train.astype(int).tolist(),
        'row_indices_test': idx_test.astype(int).tolist(),
        'n_train': int(X_train.shape[0]),
        'n_test': int(X_test.shape[0])
    }


@process()
def define_preprocess_xgb_process(data):
    """Preprocess for XGB: OHE categorical only (no scaling)."""
    src = data.get('feature_engineering_generic', {})
    df = pd.DataFrame(src['df'])
    y = np.asarray(src['labels'], dtype=int)
    idx_train = np.asarray(src['train_idx'], dtype=int)
    idx_test = np.asarray(src['test_idx'], dtype=int)

    if 'DayOfWeek' not in df.columns or 'Month' not in df.columns:
        if 'Date' in df.columns:
            dt = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
            df['DayOfWeek'] = dt.dt.weekday.fillna(0).astype(int)
            df['Month'] = dt.dt.month.fillna(1).astype(int)
        else:
            df['DayOfWeek'] = 1
            df['Month'] = 1

    cat_cols, num_cols = _get_cat_num_cols(df)
    X_df = _build_features_dataframe(df, cat_cols, num_cols)

    encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', encoder, cat_cols),
            ('num', 'passthrough', num_cols)
        ],
        remainder='drop'
    )

    X_train = preprocessor.fit_transform(X_df.iloc[idx_train])
    X_test = preprocessor.transform(X_df.iloc[idx_test])
    y_train = y[idx_train]
    y_test = y[idx_test]

    return {
        'X_train': X_train.astype(float).tolist(),
        'X_test': X_test.astype(float).tolist(),
        'y_train': y_train.astype(int).tolist(),
        'y_test': y_test.astype(int).tolist(),
        'row_indices_train': idx_train.astype(int).tolist(),
        'row_indices_test': idx_test.astype(int).tolist(),
        'n_train': int(X_train.shape[0]),
        'n_test': int(X_test.shape[0])
    }


@step()
def train_logistic_classifier(prep_data: SerializableData, hyperparameters: Dict[str, Any] | None = None) -> Dict[str, Any]:
    X_train = np.asarray(prep_data.get('X_train', []), dtype=float)
    y_train = np.asarray(prep_data.get('y_train', []), dtype=int)
    if X_train.size == 0:
        raise ValueError("Empty training data provided to Logistic training step")

    params = (hyperparameters or {}).get('logreg_params', {})
    max_iter = int(params.get('max_iter', 500))
    class_weight = params.get('class_weight', None)

    model = LogisticRegression(
        solver='lbfgs',
        max_iter=max_iter,
        class_weight=class_weight
    )
    model.fit(X_train, y_train)
    return {'model': model}


@step()
def train_and_evaluate_nn_classifier(prep_data: SerializableData, hyperparameters: Dict[str, Any] | None = None, branch_name: str = "") -> Dict[str, Any]:
    hparams = (hyperparameters or {}).get("nn_params", {})
    hidden_layers = tuple(hparams.get("hidden_layers", [128, 64]))
    learning_rate = float(hparams.get("learning_rate", 0.001))
    epochs = int(hparams.get("epochs", 50))
    random_seed = int(hparams.get("random_seed", 30))

    X_train = np.asarray(prep_data.get('X_train', []), dtype=float)
    y_train = np.asarray(prep_data.get('y_train', []), dtype=int)
    if X_train.size == 0:
        raise ValueError("Empty training data provided to NN classifier training step")

    clf = MLPClassifier(
        hidden_layer_sizes=hidden_layers,
        learning_rate_init=learning_rate,
        activation='relu',
        solver='adam',
        alpha=0.0001,
        max_iter=1,
        warm_start=True,
        early_stopping=False,
        shuffle=True,
        random_state=random_seed,
        verbose=False
    )

    for epoch in range(epochs):
        clf.fit(X_train, y_train)
        try:
            if hasattr(clf, 'loss_'):
                log_metric('train_loss', float(clf.loss_), step=epoch + 1)
            preds = clf.predict(X_train)
            f1 = float(f1_score(y_train, preds, average='macro'))
            log_metric('train_f1', f1, step=epoch + 1)
        except Exception as e:
            logger.warning(f"[{branch_name or 'nn'}] Failed to log training metrics @epoch {epoch + 1}: {e}")
    return {'model': clf}


@step()
def train_xgb_classifier(prep_data: SerializableData, hyperparameters: Dict[str, Any] | None = None) -> Dict[str, Any]:
    xgb_params = (hyperparameters or {}).get("xgb_params", {})
    params = {
        'n_estimators': int(xgb_params.get('n_estimators', 400)),
        'max_depth': int(xgb_params.get('max_depth', 4)),
        'learning_rate': float(xgb_params.get('learning_rate', 0.1)),
        'subsample': float(xgb_params.get('subsample', 0.9)),
        'colsample_bytree': float(xgb_params.get('colsample_bytree', 0.9)),
        'n_jobs': int(xgb_params.get('n_jobs', 1)),
        'verbosity': 0,
        'random_state': int(xgb_params.get('random_state', 42)) if 'random_state' in xgb_params else None,
        'tree_method': xgb_params.get('tree_method', 'auto'),
        'objective': 'multi:softprob',
        'num_class': 3,
    }

    params = {k: v for k, v in params.items() if v is not None}

    X_train = np.asarray(prep_data.get('X_train', []), dtype=float)
    y_train = np.asarray(prep_data.get('y_train', []), dtype=int)
    if X_train.size == 0:
        raise ValueError("Empty training data provided to XGB classifier training step")

    model = XGBClassifier(**params)
    model.fit(X_train, y_train)
    return {'model': model}


@step()
def test_inference_classification(model: SerializableData, X_test: SerializableData, y_test: SerializableData) -> Dict[str, Any]:
    X = np.asarray(X_test or [], dtype=float)
    y_true = np.asarray(y_test or [], dtype=int)
    if X.size == 0 or y_true.size == 0:
        try:
            log_metric('test_accuracy', 0.0)
            log_metric('test_precision', 0.0)
            log_metric('test_f1', 0.0)
        except Exception:
            pass
        return {'test_accuracy': 0.0, 'test_precision': 0.0, 'test_f1': 0.0}

    # Predict probabilities if available
    if hasattr(model, 'predict_proba'):
        proba = model.predict_proba(X)
        if isinstance(proba, list):
            proba = np.stack(proba, axis=-1)
        if proba.ndim == 3:
            proba = proba
    else:
        preds = model.predict(X)
        n_classes = len(np.unique(y_true))
        proba = np.eye(n_classes)[preds]

    y_pred = np.asarray(np.argmax(proba, axis=1), dtype=int)

    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, average='macro', zero_division=0))
    f1 = float(f1_score(y_true, y_pred, average='macro'))

    try:
        log_metric('test_accuracy', acc)
        log_metric('test_precision', prec)
        log_metric('test_f1', f1)
    except Exception:
        pass

    return {'test_accuracy': acc, 'test_precision': prec, 'test_f1': f1}


# Override training processes to consume new preprocess outputs
@process()
def define_linear_training_process(data, hyperparameters):
    prep = data.get('preprocess_linear_nn', {})
    result = train_logistic_classifier(prep_data=prep, hyperparameters=hyperparameters)
    result['X_test'] = prep.get('X_test')
    result['y_test'] = prep.get('y_test')
    result['row_indices_test'] = prep.get('row_indices_test')
    return result


@process()
def define_nn_training_process(data, hyperparameters):
    prep = data.get('preprocess_linear_nn', {})
    result = train_and_evaluate_nn_classifier(prep_data=prep, hyperparameters=hyperparameters)
    result['X_test'] = prep.get('X_test')
    result['y_test'] = prep.get('y_test')
    result['row_indices_test'] = prep.get('row_indices_test')
    return result


@process()
def define_xgb_training_process(data, hyperparameters):
    prep = data.get('preprocess_xgb', {})
    result = train_xgb_classifier(prep_data=prep, hyperparameters=hyperparameters)
    result['X_test'] = prep.get('X_test')
    result['y_test'] = prep.get('y_test')
    result['row_indices_test'] = prep.get('row_indices_test')
    return result


@process()
def define_linear_inference_process(data):
    train_res = data.get('linear_training', {})
    model = train_res.get('model')
    X_test = train_res.get('X_test')
    y_test = train_res.get('y_test')
    result = test_inference_classification(model=model, X_test=X_test, y_test=y_test)
    result['model'] = model
    result['X_test'] = X_test
    result['y_test'] = y_test
    result['row_indices_test'] = train_res.get('row_indices_test')
    result['source_training'] = 'linear_training'
    return result


@process()
def define_nn_inference_process(data, hyperparameters):
    train_key = (hyperparameters or {}).get('train_key', 'nn_training_a')
    train_res = data.get(str(train_key), {})
    model = train_res.get('model')
    X_test = train_res.get('X_test')
    y_test = train_res.get('y_test')
    result = test_inference_classification(model=model, X_test=X_test, y_test=y_test)
    result['model'] = model
    result['X_test'] = X_test
    result['y_test'] = y_test
    result['row_indices_test'] = train_res.get('row_indices_test')
    result['source_training'] = str(train_key)
    return result


@process()
def define_xgb_inference_process(data, hyperparameters):
    train_key = (hyperparameters or {}).get('train_key', 'xgb_training_a')
    train_res = data.get(str(train_key), {})
    model = train_res.get('model')
    X_test = train_res.get('X_test')
    y_test = train_res.get('y_test')
    result = test_inference_classification(model=model, X_test=X_test, y_test=y_test)
    result['model'] = model
    result['X_test'] = X_test
    result['y_test'] = y_test
    result['row_indices_test'] = train_res.get('row_indices_test')
    result['source_training'] = str(train_key)
    return result


@process()
def define_select_best_nn_process(data):
    inf_a = data.get('nn_inference_a', {}) or {}
    inf_b = data.get('nn_inference_b', {}) or {}
    f1_a = float(inf_a.get('test_f1', 0.0) or 0.0)
    f1_b = float(inf_b.get('test_f1', 0.0) or 0.0)

    best_key = 'nn_training_a'
    best_f1 = f1_a
    best_inf = inf_a
    if f1_b >= f1_a:
        best_key = 'nn_training_b'
        best_f1 = f1_b
        best_inf = inf_b

    return {
        'model': best_inf.get('model'),
        'X_test': best_inf.get('X_test'),
        'y_test': best_inf.get('y_test'),
        'row_indices_test': best_inf.get('row_indices_test'),
        'f1': best_f1,
        'best_key': best_key
    }


@process()
def define_select_best_xgb_process(data):
    inf_a = data.get('xgb_inference_a', {}) or {}
    inf_b = data.get('xgb_inference_b', {}) or {}
    f1_a = float(inf_a.get('test_f1', 0.0) or 0.0)
    f1_b = float(inf_b.get('test_f1', 0.0) or 0.0)

    best_key = 'xgb_training_a'
    best_f1 = f1_a
    best_inf = inf_a
    if f1_b >= f1_a:
        best_key = 'xgb_training_b'
        best_f1 = f1_b
        best_inf = inf_b

    return {
        'model': best_inf.get('model'),
        'X_test': best_inf.get('X_test'),
        'y_test': best_inf.get('y_test'),
        'row_indices_test': best_inf.get('row_indices_test'),
        'f1': best_f1,
        'best_key': best_key
    }


@process()
def define_nn_best_inference_process(data):
    sel = data.get('nn_best_selection', {})
    return test_inference_classification(model=sel.get('model'), X_test=sel.get('X_test'), y_test=sel.get('y_test'))


@process()
def define_xgb_best_inference_process(data):
    sel = data.get('xgb_best_selection', {})
    return test_inference_classification(model=sel.get('model'), X_test=sel.get('X_test'), y_test=sel.get('y_test'))


@process()
def define_ensemble_inference_process(data):
    lin = data.get('linear_training', {}) or {}
    xgb_sel = data.get('xgb_best_selection', {}) or {}

    lin_model = lin.get('model')
    xgb_model = xgb_sel.get('model')

    X_lin = np.asarray(lin.get('X_test') or [], dtype=float)
    y_true = np.asarray(lin.get('y_test') or [], dtype=int)
    idx_lin = np.asarray(lin.get('row_indices_test') or [], dtype=int)

    X_xgb = np.asarray(xgb_sel.get('X_test') or [], dtype=float)
    idx_xgb = np.asarray(xgb_sel.get('row_indices_test') or [], dtype=int)

    # Obtain weights from prior inferences (F1 scores)
    w_lin = float((data.get('linear_inference', {}) or {}).get('test_f1', 0.0) or 0.0)
    w_xgb = float((data.get('xgb_best_inference', {}) or {}).get('test_f1', 0.0) or 0.0)

    weights = np.array([w_lin, w_xgb], dtype=float)
    if not np.isfinite(weights).all() or weights.sum() <= 0:
        weights = np.array([1.0, 1.0], dtype=float)
    weights = weights / weights.sum()

    # Predict probabilities
    def _predict_proba_safe(m, X):
        if m is None or X.size == 0:
            return None
        if hasattr(m, 'predict_proba'):
            p = m.predict_proba(X)
            if isinstance(p, list):
                p = np.stack(p, axis=-1)
            return p
        preds = m.predict(X)
        n_classes = 3
        return np.eye(n_classes)[preds]

    P_lin = _predict_proba_safe(lin_model, X_lin)
    P_xgb = _predict_proba_safe(xgb_model, X_xgb)

    # Align by row indices if provided
    def _align_to(reference_idx, idx_other, P_other):
        if P_other is None or reference_idx.size == 0 or idx_other.size == 0:
            return None
        if np.array_equal(reference_idx, idx_other):
            return P_other
        order = {int(v): i for i, v in enumerate(idx_other.tolist())}
        aligned = np.zeros_like(P_other)
        for pos, rid in enumerate(reference_idx.tolist()):
            j = order.get(int(rid))
            if j is None:
                continue
            aligned[pos] = P_other[j]
        return aligned

    P_xgb_aligned = _align_to(idx_lin, idx_xgb, P_xgb) if P_xgb is not None else None

    # Combine probabilities (weighted soft vote)
    probas = []
    wlist = []
    if P_lin is not None:
        probas.append(P_lin)
        wlist.append(weights[0])
    if P_xgb_aligned is not None:
        probas.append(P_xgb_aligned)
        wlist.append(weights[1])

    if not probas or y_true.size == 0:
        try:
            log_metric('test_accuracy', 0.0)
            log_metric('test_precision', 0.0)
            log_metric('test_f1', 0.0)
        except Exception:
            pass
        return {'test_accuracy': 0.0, 'test_precision': 0.0, 'test_f1': 0.0}

    W = np.array(wlist, dtype=float)
    W = W / W.sum()
    stacked = np.stack(probas, axis=0)
    ens = np.tensordot(W, stacked, axes=(0, 0))
    y_pred = np.argmax(ens, axis=1).astype(int)

    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, average='macro', zero_division=0))
    f1 = float(f1_score(y_true, y_pred, average='macro'))
    try:
        log_metric('test_accuracy', acc)
        log_metric('test_precision', prec)
        log_metric('test_f1', f1)
    except Exception:
        pass
    return {'test_accuracy': acc, 'test_precision': prec, 'test_f1': f1}


