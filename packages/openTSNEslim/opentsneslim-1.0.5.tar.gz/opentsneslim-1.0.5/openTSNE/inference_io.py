import json
import pickle
from pathlib import Path
from typing import Any, Dict

import numpy as np

from openTSNE.tsne import TSNEEmbedding
from openTSNE import affinity as affinity_mod
from openTSNE import nearest_neighbors as nn_mod


def export_inference_bundle(embedding: TSNEEmbedding, bundle_path: str | Path) -> None:
    """Export a lightweight, pickle-free bundle for slim inference.

    Saves:
      - reference embedding array (Y)
      - affinity config and knn_index state (pickled and base64-encoded inside JSON)
      - optimizer/gradient params required by transform
    """
    bundle_path = Path(bundle_path)
    bundle_path.parent.mkdir(parents=True, exist_ok=True)

    Y = np.asarray(embedding)
    meta: Dict[str, Any] = {
        "affinity_class": embedding.affinities.__class__.__name__,
        "perplexity": getattr(embedding.affinities, "perplexity", None),
        "perplexities": getattr(embedding.affinities, "perplexities", None),
        "metric": getattr(embedding.affinities.knn_index, "metric", None),
        "k": getattr(embedding.affinities.knn_index, "k", None),
        "gradient_descent_params": embedding.gradient_descent_params,
        "dof": embedding.gradient_descent_params.get("dof", 1),
        "knn_class": embedding.affinities.knn_index.__class__.__name__,
    }

    # Serialize knn_index state in a pickle-in-json friendly way
    knn_state = embedding.affinities.knn_index.__getstate__()
    meta["knn_state_pickle_b64"] = pickle.dumps(knn_state).hex()

    # Save interpolation grid if present (optional for faster transform)
    aux = {}
    if getattr(embedding, "interp_coeffs", None) is not None:
        aux["interp_coeffs"] = np.asarray(embedding.interp_coeffs)
    if getattr(embedding, "box_x_lower_bounds", None) is not None:
        aux["box_x_lower_bounds"] = np.asarray(embedding.box_x_lower_bounds)
    if getattr(embedding, "box_y_lower_bounds", None) is not None:
        aux["box_y_lower_bounds"] = np.asarray(embedding.box_y_lower_bounds)

    # Write files
    np.savez_compressed(bundle_path.with_suffix(".npz"), Y=Y, **aux)
    with open(bundle_path.with_suffix(".json"), "w", encoding="utf-8") as f:
        json.dump(meta, f)


def load_inference_bundle(bundle_path: str | Path) -> TSNEEmbedding:
    """Load a slim inference bundle and reconstruct a TSNEEmbedding.

    Returns an embedding that supports .transform without requiring sklearn/scipy.
    """
    bundle_path = Path(bundle_path)
    arrays = np.load(bundle_path.with_suffix(".npz"))
    with open(bundle_path.with_suffix(".json"), "r", encoding="utf-8") as f:
        meta = json.load(f)

    Y = np.ascontiguousarray(arrays["Y"])  # reference embedding

    # Reconstruct KNN index from state
    knn_class_name = meta["knn_class"]
    knn_cls = getattr(nn_mod, knn_class_name)
    knn = knn_cls.__new__(knn_cls)  # type: ignore
    knn_state = pickle.loads(bytes.fromhex(meta["knn_state_pickle_b64"]))
    knn.__setstate__(knn_state)

    # Build affinities with provided knn (avoid symmetrization that requires scipy)
    affinity_class_name = meta["affinity_class"]
    aff_cls = getattr(affinity_mod, affinity_class_name)
    if "perplexities" in meta and meta["perplexities"] is not None:
        affinities = aff_cls(
            perplexities=meta["perplexities"], knn_index=knn, symmetrize=False
        )
    else:
        affinities = aff_cls(
            perplexity=meta.get("perplexity"), knn_index=knn, symmetrize=False
        )

    # Recreate embedding with same optimization params
    gd_params = meta.get("gradient_descent_params", {})
    from openTSNE.tsne import gradient_descent

    emb = TSNEEmbedding(
        Y.copy(),
        affinities,
        optimizer=gradient_descent(),
        **gd_params,
    )

    # Restore optional interpolation grid
    emb.interp_coeffs = arrays.get("interp_coeffs", None)
    emb.box_x_lower_bounds = arrays.get("box_x_lower_bounds", None)
    emb.box_y_lower_bounds = arrays.get("box_y_lower_bounds", None)

    return emb


