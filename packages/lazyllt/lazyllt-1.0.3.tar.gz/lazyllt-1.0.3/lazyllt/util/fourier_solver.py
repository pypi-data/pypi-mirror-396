import jax
import jax.numpy as jnp

@jax.jit
def solve_coefficients(n_list, thetas, c, alpha_geo, b, alpha_0):
    """
    Solve for the Fourier coefficients using matrix pseudo-inverses.
    :param n_list: Shape (F,)
    :param thetas: Shape (N,)
    :param c: Shape (N,)
    :param alpha_geo: Shape (N,). In radians.
    :param b: Scalar.
    :param alpha_0: Scalar. In radians.
    :return: Shape (F,)
    """
    a_i = jnp.einsum("i,j->ij", 1/jnp.sin(thetas), n_list) #Shape (N, F)
    a_i *= jnp.sin(jnp.einsum("i,j->ij", thetas, n_list))

    a_eff = jnp.sin(jnp.einsum("i,j->ij", thetas, n_list)) #Shape (N, F)
    a_eff = jnp.einsum("i,ij->ij", 1/c, a_eff) #Shape (N, F)
    a_eff *= 2 * b / jnp.pi

    #lhs @ coefficients = rhs
    lhs = a_i + a_eff #Shape (N, F)
    rhs = alpha_geo - alpha_0 #Shape (N,)

    pseudo_inverse = jnp.linalg.pinv(lhs) #Shape (F, N)

    coef = pseudo_inverse @ rhs # (F, N) @ (N, 1) = (F, 1)

    return coef.reshape(-1)

@jax.jit
def a_i_rms_error(n_list, coefficients, thetas, c, alpha_geo, b, alpha_0):
    """
    Get the RMS error in induced angle of attack (in radians) given calculated coefficients.
    :param n_list: Shape (F,)
    :param coefficients: Shape (F,)
    :param thetas: Shape (N,)
    :param c: Shape (N,)
    :param alpha_geo: Shape (N,). In radians.
    :param b: Scalar.
    :param alpha_0: Scalar. In radians.
    :return: Shape (F,)
    """
    a_i = jnp.einsum("i,j->ij", 1/jnp.sin(thetas), n_list) #Shape (N, F)
    a_i *= jnp.sin(jnp.einsum("i,j->ij", thetas, n_list))

    a_eff = jnp.sin(jnp.einsum("i,j->ij", thetas, n_list)) #Shape (N, F)
    a_eff = jnp.einsum("i,ij->ij", 1/c, a_eff) #Shape (N, F)
    a_eff *= 2 * b / jnp.pi

    #lhs @ coefficients = rhs
    lhs = a_i + a_eff #Shape (N, F)
    rhs = alpha_geo - alpha_0 #Shape (N,)

    residual = lhs @ coefficients - rhs #Shape (N,)
    rms_error = jnp.sqrt(jnp.mean(residual ** 2))

    return rms_error