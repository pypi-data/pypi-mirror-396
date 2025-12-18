from typing import Protocol, Any, runtime_checkable

# We use Any here to support numpy.ndarray, jax.Array, torch.Tensor
# from numpy.typing import ArrayLike
ArrayLike = Any 

@runtime_checkable
class PricingBackend(Protocol):
    """
    Interface for pricing kernels (CPU/GPU agnostic).
    Implementations can be Numpy (CPU), JAX (GPU/TPU), or CUDA.
    """
    def black_scholes_price(
        self, 
        S: ArrayLike, K: ArrayLike, T: ArrayLike, 
        r: ArrayLike, sigma: ArrayLike, 
        is_call: ArrayLike
    ) -> ArrayLike:
        ...
        #TODO: Implement this method in concrete backends
        # like the nbs module

    def implied_volatility(
        self, 
        price: ArrayLike, S: ArrayLike, K: ArrayLike, 
        T: ArrayLike, r: ArrayLike, 
        is_call: ArrayLike
    ) -> ArrayLike:
        ...

