import os
import tempfile

import numpy as np

from openTSNE.affinity import PerplexityBasedNN
from openTSNE.initialization import random as init_random
from openTSNE.tsne import TSNEEmbedding, gradient_descent
from openTSNE.inference_io import export_inference_bundle, load_inference_bundle


def test_transform_smoke_without_sklearn_scipy():
    # Reference data and embedding
    rng = np.random.RandomState(42)
    X_ref = rng.normal(size=(200, 8)).astype(np.float32)

    # Build affinities using Annoy (no sklearn/scipy)
    aff = PerplexityBasedNN(
        data=X_ref,
        perplexity=30,
        method="annoy",
        symmetrize=False,
        n_jobs=1,
        verbose=False,
    )

    # Create a tiny embedding without running optimization
    Y0 = init_random(X_ref, n_components=2, random_state=0)
    emb = TSNEEmbedding(
        Y0,
        aff,
        optimizer=gradient_descent(),
        negative_gradient_method="bh",
        dof=1,
        n_jobs=1,
    )

    # Export and reload via slim bundle
    with tempfile.TemporaryDirectory() as d:
        bundle_base = os.path.join(d, "tsne_slim_bundle")
        export_inference_bundle(emb, bundle_base)
        emb2 = load_inference_bundle(bundle_base)

    # Transform a few new points
    X_new = rng.normal(size=(25, 8)).astype(np.float32)
    partial = emb2.transform(
        X_new,
        perplexity=5,
        initialization="median",
        k=15,
        n_iter=10,
        early_exaggeration_iter=0,
        learning_rate=0.1,
        max_grad_norm=0.5,
    )

    assert partial.shape == (25, 2)


