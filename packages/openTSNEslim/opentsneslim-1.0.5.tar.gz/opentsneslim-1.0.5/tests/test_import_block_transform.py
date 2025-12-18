import importlib.abc
import os
import numpy as np


class _Blocker(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        root = fullname.split(".", 1)[0]
        if root in {"sklearn", "scipy"}:
            raise ImportError(f"blocked import: {fullname}")
        return None


def test_transform_path_works_with_blocked_sklearn_scipy(monkeypatch):
    # Install import blocker so any attempt to import sklearn/scipy fails
    import sys

    sys.meta_path.insert(0, _Blocker())

    # Optional: deliberately try to import sklearn to demonstrate failure
    # Set TRY_IMPORT_SKLEARN=1 to force this test to fail on import
    if os.environ.get("TRY_IMPORT_SKLEARN") == "1":
        import sklearn  # noqa: F401  # this should be blocked and raise ImportError

    from openTSNE.affinity import PerplexityBasedNN
    from openTSNE.initialization import random as init_random
    from openTSNE.tsne import TSNEEmbedding, gradient_descent

    rng = np.random.RandomState(0)
    X_ref = rng.normal(size=(150, 6)).astype(np.float32)

    # Use Annoy backend (vendored) to avoid sklearn/scipy
    aff = PerplexityBasedNN(
        data=X_ref,
        perplexity=20,
        method="annoy",
        symmetrize=False,
        n_jobs=1,
        verbose=False,
    )

    Y0 = init_random(X_ref, n_components=2, random_state=0)
    emb = TSNEEmbedding(
        Y0,
        aff,
        optimizer=gradient_descent(),
        negative_gradient_method="bh",
        dof=1,
        n_jobs=1,
    )

    X_new = rng.normal(size=(12, 6)).astype(np.float32)
    partial = emb.transform(
        X_new,
        perplexity=5,
        initialization="median",
        k=15,
        n_iter=8,
        early_exaggeration_iter=0,
        learning_rate=0.1,
        max_grad_norm=0.5,
    )

    assert partial.shape == (12, 2)


