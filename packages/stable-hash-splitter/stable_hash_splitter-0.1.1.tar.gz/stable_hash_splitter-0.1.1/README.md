# Stable Hash Splitter

StableHashSplit provides deterministic, ID-based train/test splits so samples remain assigned to the same set across dataset updates. This prevents data leakage that can occur when old test samples reappear in training after you refresh or append data.

Key goals:
- Reproducible splits across dataset versions
- Seamless scikit-learn compatibility (CV and pipelines)
- Minimal and flexible API for common workflows

Features
- Deterministic & stable assignment using a hash of a stable identifier
- scikit-learn compatible: implements `split` and `get_n_splits`
- Works with pandas DataFrames, NumPy arrays, and array-likes
- Customizable hash function and ID column; supports using the DataFrame index

Installation

```bash
pip install stable-hash-splitter
```

Quick start

```python
import pandas as pd
from stable_hash_splitter import StableHashSplit

data = pd.DataFrame({
    'user_id': [1001, 1002, 1003, 1004, 1005],
    'feature_1': [0.5, 0.3, 0.8, 0.1, 0.9],
    'feature_2': [10, 20, 30, 40, 50],
    'target': [1, 0, 1, 0, 1]
})

splitter = StableHashSplit(test_size=0.2, id_column='user_id')
X_train, X_test, y_train, y_test = splitter.train_test_split(
    data[['user_id', 'feature_1', 'feature_2']],
    data['target']
)

print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
```

API reference

StableHashSplit(test_size=0.2, id_column='id', hash_func=None, random_state=None)

- `test_size` (float): fraction of samples assigned to the test set (0 < test_size < 1).
- `id_column` (str | int | None): column name or index with the stable identifier. If `None` and `X` is a DataFrame, the DataFrame index is used.
- `hash_func` (callable): function that maps an identifier to a non-negative integer hash. Defaults to CRC32.
- `random_state`: accepted for API compatibility but ignored; splits are deterministic.

Important notes
- Deterministic: the same ID always maps to the same split.
- For array inputs with no `id_column` provided, row indices are used as identifiers.
- The class yields a single split (compatible with scikit-learn CV APIs).

Example: use in GridSearchCV

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV

splitter = StableHashSplit(test_size=0.2, id_column='user_id')
model = RandomForestClassifier()

param_grid = {'n_estimators': [50, 100]}
grid_search = GridSearchCV(model, param_grid, cv=splitter)
grid_search.fit(X, y)  # X must include the 'user_id' column
```

Development & testing

Install in editable mode to develop locally:

```bash
pip install -e .
pip install pytest
pytest
```

Attribution

The concept and motivation for ID-based deterministic splits are inspired by Aurélien Géron's book "Hands-On Machine Learning with Scikit-Learn and PyTorch". This project is an independent implementation and not a copy of that work; the book influenced design patterns and best practices used here.

Contributing

Contributions welcome — please open issues or submit pull requests. See `PUBLISH.md` for publishing steps and CI instructions.

License

MIT — see the `LICENSE` file.
# Stable Hash Splitter

A scikit-learn compatible splitter for deterministic, ID-based train/test splits. StableHashSplit prevents data leakage by assigning samples to train/test permanently based on a hash of a stable identifier (e.g., user ID, transaction ID).
## 🔧 Problem

Using random splits when datasets change can cause previous test samples to move into training sets, producing optimistic and invalid evaluations. `StableHashSplit` ensures reproducible, ID-based assignment so samples remain in the same split across dataset versions.
## ✨ Features

- **Deterministic & Stable:** A given ID is always placed in the same set.
- **scikit-learn Compatible:** Works with `cross_val_score`, `GridSearchCV`, and pipelines expecting a CV splitter.
## 📦 Installation

```bash
pip install stable-hash-splitter
```

## 🚀 Quick Start

```python
import pandas as pd
from stable_hash_splitter import StableHashSplit

data = pd.DataFrame({
	'user_id': [1001, 1002, 1003, 1004, 1005],
	'feature_1': [0.5, 0.3, 0.8, 0.1, 0.9],
	'feature_2': [10, 20, 30, 40, 50],
	'target': [1, 0, 1, 0, 1]
})

splitter = StableHashSplit(test_size=0.2, id_column='user_id')
X_train, X_test, y_train, y_test = splitter.train_test_split(
	data[['user_id', 'feature_1', 'feature_2']],
	data['target']
)
print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
```

## 📚 Advanced Usage

Use in model selection with `GridSearchCV`:

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV

splitter = StableHashSplit(test_size=0.2, id_column='user_id')
model = RandomForestClassifier()

param_grid = {'n_estimators': [50, 100]}
grid_search = GridSearchCV(model, param_grid, cv=splitter)
grid_search.fit(X, y)  # X must contain the 'user_id' column
```

## 🤝 Contributing

Contributions welcome — please open an issue or submit a pull request.

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## 🔧 Developing & Testing Locally

1. Install in editable mode:

```bash
pip install -e .
```

2. Run tests:

```bash
pytest
```
# Stable Hash Splitter

A scikit-learn compatible splitter for **deterministic, ID-based train/test splits**. Solves the critical problem of data leakage when datasets grow or models are retrained, ensuring a data sample is **permanently** assigned to the same set based on a hash of its unique identifier.

## 🔧 The Problem
When you update your dataset and retrain a model, using a standard random split (like `sklearn.model_selection.train_test_split`) can cause **data leakage**: samples that were in your old test set can end up in your new training set, making your evaluation overly optimistic and invalid.

**StableHashSplit** fixes this by assigning samples to the train or test set **deterministically** based on a hash of a stable ID (like a user ID, transaction ID, or geographic coordinate).

## ✨ Features
*   **🔒 Deterministic & Stable**: A given ID will always be placed in the same set.
*   **🤖 Full scikit-learn Compatibility**: Can be used in `cross_val_score`, `GridSearchCV`, and any pipeline expecting a CV splitter.
*   **📁 Flexible Input**: Works with pandas DataFrames, NumPy arrays, and any array-like structure.
*   **⚙️ Configurable**: Use any hash function and specify the ID column by name or index.

## 📦 Installation

```bash
pip install stable-hash-splitter