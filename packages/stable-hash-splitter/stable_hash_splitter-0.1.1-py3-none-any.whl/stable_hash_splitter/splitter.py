"""
stable_hash_splitter.splitter
=============================
Provides the StableHashSplit class for deterministic dataset splitting.
"""
import numpy as np
import pandas as pd
from zlib import crc32
from sklearn.model_selection import BaseCrossValidator
from sklearn.utils.validation import check_array, check_consistent_length

class StableHashSplit(BaseCrossValidator):
    """
    A deterministic train/test splitter based on hashing a stable identifier.

    This splitter ensures that any data sample is permanently assigned to
    either the training or test set based on a hash of its identifier. This
    prevents data leakage when datasets are updated or models are retrained,
    as old test samples will never move into the training set.

    Parameters
    ----------
    test_size : float, default=0.2
        The proportion of the dataset to include in the test split.
        Should be between 0.0 and 1.0.

    id_column : str or int, default='id'
        The name (if X is a DataFrame) or index (if X is a 2D array) of the
        column containing the stable identifier. If `None`, the identifier
        is assumed to be the index of X.

    hash_func : callable, default=None
        A function that takes an identifier and returns an integer hash.
        Defaults to CRC32 via `zlib.crc32`. The function must return a
        non-negative integer.

    random_state : int, default=None
        For compatibility with scikit-learn interfaces. Has no effect on the
        split, as it is deterministic based on the hash. A warning is issued
        if provided.

    Attributes
    ----------
    n_splits : int
        Always returns 1, as this is a single split iterator.
    """

    def __init__(self, test_size=0.2, id_column='id', hash_func=None, random_state=None):
        if not (0.0 < test_size < 1.0):
            raise ValueError(f"test_size must be between 0.0 and 1.0. Got {test_size}")

        self.test_size = test_size
        self.id_column = id_column
        self.hash_func = hash_func
        self.random_state = random_state

        if random_state is not None:
            import warnings
            warnings.warn(
                "`random_state` is set but has no effect on StableHashSplit, as splits are deterministic.",
                UserWarning
            )

        # Set default hash function (CRC32)
        if self.hash_func is None:
            self.hash_func = lambda x: crc32(str(x).encode()) & 0xffffffff  # Ensure non-negative

        self._max_hash = 2**32

    def _get_identifiers(self, X):
        """Extract the identifier series from X (DataFrame, array, or Series)."""
        if isinstance(X, pd.DataFrame):
            if self.id_column in X.columns:
                return X[self.id_column]
            else:
                raise ValueError(f"ID column '{self.id_column}' not found in DataFrame.")
        elif isinstance(X, pd.Series):
            return X
        else:  # Assume it's a 2D array
            X_array = check_array(X, ensure_2d=True)
            if isinstance(self.id_column, int):
                if X_array.shape[1] > self.id_column:
                    return X_array[:, self.id_column]
                else:
                    raise ValueError(f"Column index {self.id_column} out of bounds for array with {X_array.shape[1]} columns.")
            else:
                # If no column specified and X is an array, use row indices
                return pd.RangeIndex(0, X_array.shape[0])

    def _in_test_set(self, identifier):
        """Determine if an identifier belongs to the test set."""
        hash_val = self.hash_func(identifier)
        # Compare hash to threshold (e.g., 20% of max hash value)
        return hash_val < self.test_size * self._max_hash

    def split(self, X, y=None, groups=None):
        """
        Generate indices to split data into training and test set.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features) or DataFrame
            Training data, which includes the identifier column.

        y : array-like of shape (n_samples,)
            Always ignored, exists for compatibility.

        groups : array-like of shape (n_samples,)
            Always ignored, exists for compatibility.

        Yields
        ------
        train_indices : ndarray
            The training set indices for that split.

        test_indices : ndarray
            The testing set indices for that split.
        """
        ids = self._get_identifiers(X)

        # Create boolean mask for the test set
        test_mask = ids.apply(self._in_test_set) if isinstance(ids, pd.Series) else np.array([self._in_test_set(id_) for id_ in ids])

        train_indices = np.where(~test_mask)[0]
        test_indices = np.where(test_mask)[0]

        # Yield the single split (this makes it compatible with cross-validation iterators)
        yield (train_indices, test_indices)

    def get_n_splits(self, X=None, y=None, groups=None):
        """Returns the number of splitting iterations (always 1 for a single split)."""
        return 1

    # Convenience method for a simple one-off split (like train_test_split)
    def train_test_split(self, X, y=None, **kwargs):
        """
        Split data into random train and test subsets, deterministically based on ID hash.

        This is a convenience wrapper that mimics the signature of
        `sklearn.model_selection.train_test_split`.

        Returns
        -------
        X_train, X_test, [y_train, y_test] : list of arrays or DataFrames
            The split data. If `y` is provided, it is also split accordingly.
        """
        from sklearn.model_selection import train_test_split as sk_split

        check_consistent_length(X, y)
        train_idx, test_idx = next(self.split(X))

        if y is not None:
            if isinstance(X, pd.DataFrame):
                return X.iloc[train_idx], X.iloc[test_idx], y.iloc[train_idx], y.iloc[test_idx]
            else:
                return X[train_idx], X[test_idx], y[train_idx], y[test_idx]
        else:
            if isinstance(X, pd.DataFrame):
                return X.iloc[train_idx], X.iloc[test_idx]
            else:
                return X[train_idx], X[test_idx]