import pytest
import pandas as pd
import numpy as np
from stable_hash_splitter import StableHashSplit


def test_split_returns_correct_sizes():
    data = pd.DataFrame({'id': range(100), 'val': np.random.randn(100)})
    splitter = StableHashSplit(test_size=0.25, id_column='id')
    X_train, X_test = splitter.train_test_split(data)
    assert len(X_train) + len(X_test) == 100
    # Allow reasonable variance due to hashing randomness for finite samples
    assert abs(len(X_test) - 25) <= 6


def test_split_is_deterministic():
    data = pd.DataFrame({'id': [42, 101, 7, 256], 'val': [1, 2, 3, 4]})
    splitter = StableHashSplit(test_size=0.5, id_column='id')
    train1, test1 = splitter.train_test_split(data)
    train2, test2 = splitter.train_test_split(data)
    pd.testing.assert_frame_equal(train1, train2)
    pd.testing.assert_frame_equal(test1, test2)


def test_works_with_sklearn_cv():
    from sklearn.model_selection import cross_val_score
    from sklearn.dummy import DummyClassifier

    data = pd.DataFrame({'id': range(50), 'feature': np.random.randn(50), 'target': np.random.randint(0, 2, 50)})
    splitter = StableHashSplit(test_size=0.2, id_column='id')
    model = DummyClassifier()
    # This should run without error
    scores = cross_val_score(model, data[['id', 'feature']], data['target'], cv=splitter)
    assert len(scores) == 1  # Our splitter yields one CV fold
