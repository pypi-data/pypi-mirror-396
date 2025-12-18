
from .backend import PricingBackend

_BACKENDS = {}

def register_backend(name: str, backend: PricingBackend):
    _BACKENDS[name] = backend

def get_engine(name: str = "numpy") -> PricingBackend:
    if name not in _BACKENDS:
        if name == "numpy":
            from .backends.numpy import NumpyBackend
            return NumpyBackend()
        elif name == "jax":
            # # raise error if jax not installed
            # from .backends.jax import JaxBackend
            # return JaxBackend()
            # Future expansion
            raise ImportError("JAX backend not installed. pip install optds-iv-jax")
        elif name == "cuda":
            # import cupy
            # from .backends.cuda import CudaBackend
            # return CudaBackend()
            raise ImportError("CUDA backend not installed. pip install optds-iv-cuda")
    return _BACKENDS[name]
