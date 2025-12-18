import numpy as np


class LightCSR:
    """Minimal CSR container sufficient for opentsne transform path.

    Provides .data, .indices, .indptr, .shape and in-place scale operations.
    """

    def __init__(self, data, indices, indptr, shape):
        self.data = np.asarray(data, dtype=float)
        self.indices = np.asarray(indices, dtype=np.int32)
        self.indptr = np.asarray(indptr, dtype=np.int32)
        self.shape = tuple(shape)

    def __imul__(self, s):
        self.data *= s
        return self

    def __itruediv__(self, s):
        self.data /= s
        return self


