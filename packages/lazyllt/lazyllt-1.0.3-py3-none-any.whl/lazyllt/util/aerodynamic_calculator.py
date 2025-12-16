"""
A collection of pure functions used to calculate wing properties.
"""

import jax
import jax.numpy as jnp

@jax.jit
def wing_area_ar(thetas, b, c):
    z = -(b / 2) * jnp.cos(thetas)
    area = jnp.trapezoid(y=c, x=z)
    ar = b ** 2 / area

    return jnp.array([area, ar])

@jax.jit
def cl(coefficients, aspect_ratio):
    return coefficients[0] * jnp.pi * aspect_ratio

@jax.jit
def cdi(cl, efficiency, aspect_ratio):
    return cl ** 2 / (efficiency * jnp.pi * aspect_ratio)

@jax.jit
def efficiency(n_list, coefficients):
    a1 = coefficients[0]

    delta = jnp.einsum("i,i->", n_list[1:], (coefficients[1:] / a1) ** 2)

    return 1 / (1 + delta)

@jax.jit
def lift(cl, wing_area, rho, v_infty):
    return 0.5 * cl * wing_area * rho * v_infty ** 2

@jax.jit
def induced_drag(cdi, wing_area, rho, v_infty):
    return 0.5 * cdi * wing_area * rho * v_infty ** 2

@jax.jit
def unitless_circulation(n_list, thetas, coefficients):
    gamma = jnp.sin(jnp.einsum("i,j->ij", thetas, n_list))  # Shape (N, F)
    gamma = jnp.einsum("j,ij->i", coefficients, gamma)  # Shape (N,)

    return gamma

@jax.jit
def alpha_induced(n_list, thetas, coefficients):
    terms_1 = jnp.einsum("i,j,j->ij", 1 / jnp.sin(thetas), coefficients, n_list)  # Shape (N, F)
    terms_2 = jnp.sin(jnp.einsum("i,j->ij", thetas, n_list))  # Shape (N, F)

    a_i = jnp.einsum("ij,ij->i", terms_1, terms_2)  # Shape (N,)

    return a_i