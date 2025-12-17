from sklearn.metrics import accuracy_score, precision_score 
import sys
from pathlib import Path
from typing import Dict, Any
import logging
import numpy as np
from sklearn.linear_model import LogisticRegression
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, precision_score
from sklearn.metrics import log_loss

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from mlops.core import (
    step, process,
    SerializableData, log_metric
)


logger = logging.getLogger(__name__)

def _titanic_csv_path() -> Path:
    return Path(__file__).parent.parent / "data" / "Titanic-Dataset.csv"
    #return Path("/home/e/e0958526/mlops-platform/projects/titanic/data/Titanic-Dataset.csv")


@step()
def train_and_evaluate_nn(prep_data: SerializableData, hyperparameters: Dict[str, Any], branch_name: str = "") -> Dict[str, Any]:
    """
    Train a simple neural network classifier using scikit-learn MLPClassifier.
    Logs `train_loss` per epoch for dynamic charts.
    """

    nn_params = (hyperparameters or {}).get("nn_params", {})
    hidden_layers = tuple(nn_params.get("hidden_layers", [64, 32]))
    learning_rate = float(nn_params.get("learning_rate", 0.01))
    epochs = int(nn_params.get("epochs", 50))
    batch_size = int(nn_params.get("batch_size", 64))

    X_train = np.asarray(prep_data.get('X_train', []), dtype=float)
    y_train = np.asarray(prep_data.get('y_train', []), dtype=int)
    X_val = np.asarray(prep_data.get('X_test', []), dtype=float)
    y_val = np.asarray(prep_data.get('y_test', []), dtype=int)

    try:
        logger.info(f"[{branch_name}] prep_data keys: {list(prep_data.keys())}")
        logger.info(
            f"[{branch_name}] lens -> X_train={len(prep_data.get('X_train', []))}, "
            f"X_test={len(prep_data.get('X_test', []))}, "
            f"y_train={len(prep_data.get('y_train', []))}, "
            f"y_test={len(prep_data.get('y_test', []))}"
        )
        logger.info(
            f"[{branch_name}] array shapes -> X_train={getattr(X_train, 'shape', None)}, "
            f"X_val={getattr(X_val, 'shape', None)}"
        )
    except Exception:
        pass

    if X_train.size == 0 or X_val.size == 0:
        try:
            sizes_detail = {
                'len_X_train_list': len(prep_data.get('X_train', [])),
                'len_X_test_list': len(prep_data.get('X_test', [])),
                'len_y_train_list': len(prep_data.get('y_train', [])),
                'len_y_test_list': len(prep_data.get('y_test', [])),
                'X_train_shape': getattr(X_train, 'shape', None),
                'X_val_shape': getattr(X_val, 'shape', None),
                'prep_keys': list(prep_data.keys()),
            }
        except Exception:
            sizes_detail = {}
        raise ValueError(f"Empty training or validation data provided to NN training step; details={sizes_detail}")

    clf = MLPClassifier(
        hidden_layer_sizes=hidden_layers,
        learning_rate_init=learning_rate,
        solver='adam',
        activation='relu',
        alpha=0.0001,
        batch_size=min(batch_size, X_train.shape[0]),
        max_iter=1,
        warm_start=False,
        verbose=False
    )

    n_samples = X_train.shape[0]
    indices = np.arange(n_samples)
    losses = []

    classes_for_training = np.array([0, 1], dtype=int)

    for epoch in range(epochs):
        np.random.shuffle(indices)
        X_train_shuffled = X_train[indices]
        y_train_shuffled = y_train[indices]

        start = 0
        while start < n_samples:
            end = min(start + batch_size, n_samples)
            X_batch = X_train_shuffled[start:end]
            y_batch = y_train_shuffled[start:end]
            clf.partial_fit(X_batch, y_batch, classes=classes_for_training)
            start = end

        probs = clf.predict_proba(X_train)
        loss_val = float(log_loss(y_train, probs, labels=getattr(clf, 'classes_', [0, 1])))
        losses.append(loss_val)
        try:
            log_metric('train_loss', loss_val, step=epoch + 1)
        except Exception as e:
            logger.warning(f"[{branch_name}] Failed to log train_loss at epoch {epoch + 1}: {e}")

    y_pred = clf.predict(X_val)
    acc = float(accuracy_score(y_val, y_pred))
    prec = float(precision_score(y_val, y_pred, zero_division=0))

    try:
        log_metric('final_accuracy', acc)
        log_metric('final_precision', prec)
    except Exception as e:
        logger.warning(f"[{branch_name}] Failed to log final NN metrics: {e}")

    model = clf
    return {
        'model': model
    }


@step()
def train_linear(prep_data: SerializableData, hyperparameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Train a Logistic Regression classifier.
    """

    linear_params = (hyperparameters or {}).get("linear_params", {})
    C = float(linear_params.get('C', 0.9))
    penalty = str(linear_params.get('penalty', 'l2'))
    solver = str(linear_params.get('solver', 'lbfgs'))
    max_iter = int(linear_params.get('max_iter', 200))

    X_train = np.asarray(prep_data.get('X_train', []), dtype=float)
    y_train = np.asarray(prep_data.get('y_train', []), dtype=int)
    X_val = np.asarray(prep_data.get('X_test', []), dtype=float)
    y_val = np.asarray(prep_data.get('y_test', []), dtype=int)

    if X_train.size == 0 or X_val.size == 0:
        raise ValueError("Empty training or validation data provided to Linear model training step")

    clf = LogisticRegression(C=C, penalty=penalty, solver=solver, max_iter=max_iter)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_val)
    acc = float(accuracy_score(y_val, y_pred))
    prec = float(precision_score(y_val, y_pred, zero_division=0))

    try:
        log_metric('final_accuracy', acc)
        log_metric('final_precision', prec)
    except Exception as e:
        logger.warning(f"[Linear] Failed to log final Linear metrics: {e}")

    return {
        'model': clf
    }


@step()
def test_inference(model: SerializableData, X_test: SerializableData, y_test: SerializableData) -> Dict[str, Any]:
    """
    Run test inference and compute accuracy and precision.
    """

    X = np.asarray(X_test, dtype=float)
    y_list = list(y_test or [])
    keep_indices = []
    y_coerced = []
    for idx, val in enumerate(y_list):
        try:
            y_coerced.append(int(val))
            keep_indices.append(idx)
        except Exception:
            continue
    if keep_indices and len(keep_indices) != len(y_list):
        X = X[keep_indices]
    y_true = np.asarray(y_coerced, dtype=int)
    y_pred = model.predict(X) if len(X) > 0 else np.array([], dtype=int)

    acc = float(accuracy_score(y_true, y_pred)) if len(y_true) > 0 else 0.0
    prec = float(precision_score(y_true, y_pred, zero_division=0)) if len(y_true) > 0 else 0.0

    try:
        log_metric('test_accuracy', acc)
        log_metric('test_precision', prec)
    except Exception as e:
        logger.warning(f"Failed to log test metrics: {e}")

    return {
        'test_accuracy': acc,
        'test_precision': prec
    }


@process(logging=False)
def define_data_preprocessing_process(data, hyperparameters):
    """Load CSV, clean, engineer features, encode, split."""

    @step()
    def load_csv() -> SerializableData:
        path = _titanic_csv_path()
        try:
            logger.info(f"[data_preprocessing.load_csv] Reading CSV from: {path}")
        except Exception:
            pass
        if not path.exists():
            raise FileNotFoundError(f"Titanic CSV not found at {path}")
        df = pd.read_csv(path)
        try:
            logger.info(f"[data_preprocessing.load_csv] Loaded df shape: {df.shape}")
        except Exception:
            pass
        return {'df': df.to_dict(orient='list')}

    @step()
    def clean_and_engineer(raw: SerializableData) -> SerializableData:
        import pandas as pd
        df = pd.DataFrame(raw['df'])
        try:
            logger.info(f"[data_preprocessing.clean_and_engineer] Input columns: {list(df.columns)}")
        except Exception:
            pass

        # Basic cleaning
        # Fill Embarked missing with mode
        if 'Embarked' in df.columns:
            embarked_mode = df['Embarked'].mode(dropna=True)
            df['Embarked'] = df['Embarked'].fillna(embarked_mode.iloc[0] if not embarked_mode.empty else 'S')
        # Fill Fare missing with median
        if 'Fare' in df.columns:
            df['Fare'] = df['Fare'].fillna(df['Fare'].median())

        # Extract Title from Name
        if 'Name' in df.columns:
            df['Title'] = df['Name'].str.extract(r',\s*([^\.]+)\.', expand=False).str.strip()
            # Normalize rare titles
            common = {'Mr', 'Mrs', 'Miss', 'Master'}
            df['Title'] = df['Title'].apply(lambda t: t if t in common else 'Rare')
        else:
            df['Title'] = 'Mr'

        # Family features
        df['FamilySize'] = df.get('SibSp', 0) + df.get('Parch', 0) + 1
        df['IsAlone'] = (df['FamilySize'] == 1).astype(int)

        # Age imputation by Title median
        if 'Age' in df.columns:
            df['Age'] = df['Age'].astype(float)
            df['Age'] = df.groupby('Title')['Age'].transform(lambda s: s.fillna(s.median()))
            df['Age'] = df['Age'].fillna(df['Age'].median())

        # Keep only relevant columns
        cols = ['Survived', 'Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare', 'Embarked', 'Title', 'FamilySize', 'IsAlone']
        df = df[[c for c in cols if c in df.columns]].copy()
        try:
            logger.info(f"[data_preprocessing.clean_and_engineer] Output columns: {list(df.columns)}, shape: {df.shape}")
        except Exception:
            pass
        return {'df': df.to_dict(orient='list')}

    @step()
    def encode_and_split(raw: SerializableData, hyperparameters: Dict[str, Any] = None) -> SerializableData:
        hparams = hyperparameters
        
        df = pd.DataFrame(raw['df'])
        
        required = {'Survived', 'Sex', 'Pclass'}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns for Titanic preprocessing: {missing}")

        y = df['Survived'].astype(int).to_numpy()

        cat_cols = [c for c in ['Sex', 'Embarked', 'Title', 'Pclass'] if c in df.columns]
        num_cols = [c for c in ['Age', 'SibSp', 'Parch', 'Fare', 'FamilySize', 'IsAlone'] if c in df.columns]

        X_df = df[cat_cols + num_cols].copy()
        try:
            logger.info(
                f"[data_preprocessing.encode_and_split] cat_cols={cat_cols}, num_cols={num_cols}, X_df shape={X_df.shape}"
            )
        except Exception:
            pass
        for c in cat_cols:
            X_df[c] = X_df[c].astype(str)

        encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)

        preprocessor = ColumnTransformer(
            transformers=[
                ('cat', encoder, cat_cols),
                ('num', StandardScaler(), num_cols)
            ],
            remainder='drop'
        )

        X_all = preprocessor.fit_transform(X_df)
        try:
            logger.info(f"[data_preprocessing.encode_and_split] Encoded X_all shape: {getattr(X_all, 'shape', None)}")
        except Exception:
            pass

        test_size = float(hparams.get('test_size', 0.2))
        stratify = y if len(np.unique(y)) > 1 else None
        X_train, X_test, y_train, y_test = train_test_split(
            X_all, y, test_size=test_size, stratify=stratify
        )

        try:
            logger.info(
                f"[data_preprocessing.encode_and_split] Splits -> X_train={X_train.shape}, X_test={X_test.shape}, "
                f"y_train={y_train.shape}, y_test={y_test.shape}"
            )
        except Exception:
            pass

        return {
            'X_train': X_train.astype(float).tolist(),
            'X_test': X_test.astype(float).tolist(),
            'y_train': y_train.astype(int).tolist(),
            'y_test': y_test.astype(int).tolist(),
            'n_train': int(X_train.shape[0]),
            'n_test': int(X_test.shape[0])
        }

    raw_df = load_csv()
    engineered = clean_and_engineer(raw=raw_df)
    split = encode_and_split(raw=engineered, hyperparameters=hyperparameters)
    return split


@process()
def define_nn_training_process(data, hyperparameters):
    """NN Training process"""
    prep = data.get('data_preprocessing', {})
    result = train_and_evaluate_nn(prep_data=prep, hyperparameters=hyperparameters)
    result['X_test'] = prep.get('X_test')
    result['y_test'] = prep.get('y_test')
    return result


@process()
def define_linear_training_process(data, hyperparameters):
    """Linear model training process."""
    prep = data.get('data_preprocessing', {})
    result = train_linear(prep_data=prep, hyperparameters=hyperparameters)
    result['X_test'] = prep.get('X_test')
    result['y_test'] = prep.get('y_test')
    return result 


@process()
def define_nn_a_inference_process(data):
    """Inference on test set for NN A."""
    train_res = data.get('nn_training_a', {})
    model = train_res.get('model')
    X_test = train_res.get('X_test')
    y_test = train_res.get('y_test')

    result = test_inference(model=model, X_test=X_test, y_test=y_test)
    return result


@process()
def define_nn_b_inference_process(data):
    """Inference on test set for NN B."""
    train_res = data.get('nn_training_b', {})
    model = train_res.get('model')
    X_test = train_res.get('X_test')
    y_test = train_res.get('y_test')

    result = test_inference(model=model, X_test=X_test, y_test=y_test)
    return result


@process()
def define_linear_inference_process(data):
    """Inference on test set for Linear model."""
    train_res = data.get('linear_training', {})
    model = train_res.get('model')
    X_test = train_res.get('X_test')
    y_test = train_res.get('y_test')

    result = test_inference(model=model, X_test=X_test, y_test=y_test)
    return result