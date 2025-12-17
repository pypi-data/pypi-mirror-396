import jax
import jax.numpy as jnp
from typing import List
from collections.abc import Generator
from jaxtyping import Float, Array

from .solution import LiftingLineSolution
from .wing import UnsweptWing
from .util.fourier_solver import solve_coefficients
from .util import aerodynamic_calculator as calc


class LiftingLineModel:
    n_list: Float[Array, "F"]
    wings: List[UnsweptWing]

    def __init__(self, num_coefficients: int = 35):
        """
        A class used to manage the lifting-line problem.
        :param num_coefficients: The number of Fourier coefficients to use in the solver. Must be at least 1.
        """

        #The solver only uses the odd Fourier coefficients to ensure symmetry.
        self.n_list = jnp.arange(1, num_coefficients * 2 + 1, 2) #Shape (F,)

        self.wings = []

    def add_wing(self, wing: UnsweptWing):
        self.wings.append(wing)

    def get_wings(self) -> List[UnsweptWing]:
        return self.wings

    def solve(self, calculate_gradients=False) -> Generator[LiftingLineSolution, None, None]:
        """
        Lazily calculates the lifting-line solution for each of the given wings.
        Throws an error if no wings have been added to the model.
        :param calculate_gradients: Whether to calculate gradients or not. Disabled by default, useful for optimization.
        :return: A generator yielding LiftingLineSolution(s).
        """
        if len(self.wings) < 1:
            raise ValueError("The model does not have any loaded wings. Try calling add_wing.")

        if calculate_gradients:
            coefficients_grad = jax.jit(jax.jacrev(solve_coefficients, argnums=(2, 3, 4, 5)))
            area_ar_grad = jax.jit(jax.jacrev(calc.wing_area_ar, argnums=(1, 2)))
        else:
            coefficients_grad = lambda: None
            area_ar_grad = lambda: None

        for wing in self.wings:
            #Get the Fourier coefficients
            coefficients = solve_coefficients(self.n_list, wing.thetas, wing.c, wing.alpha_geo, wing.b, wing.alpha_0)

            if calculate_gradients:
                #Calculate gradients wrt Fourier coefficients
                c_grad, a_geo_grad, b_grad, a_0_grad = coefficients_grad(self.n_list, wing.thetas, wing.c, wing.alpha_geo, wing.b, wing.alpha_0)
                #Convert all angle gradients to degrees
                #Since all the gradients are in units rad^-1, they must be divided by the rad2deg multiplier
                a_geo_grad = jnp.deg2rad(a_geo_grad)
                a_0_grad = jnp.deg2rad(a_0_grad)
                #Calculate gradients wrt wing area and ar
                (b_grad_area, b_grad_ar), (c_grad_area, c_grad_ar) = area_ar_grad(wing.thetas, wing.b, wing.c)

                #Populate the gradients wrt scalar variables
                #The gradient dictionary is indexed first by a value, then by the variable wrt it is differentiated.
                gradients = dict()
                gradients["coefficients"] = dict()
                gradients["area"] = dict()
                gradients["aspect_ratio"] = dict()

                gradients["coefficients"]["b"] = b_grad
                gradients["area"]["b"] = b_grad_area
                gradients["aspect_ratio"]["b"] = b_grad_ar
                gradients["coefficients"]["alpha_0"] = a_0_grad

                #Calculate the parametric gradients wrt Fourier coefficients
                for parameter, param_grad in wing.taper_gradient().items():
                    #param_grad is of shape (N,).
                    #c_grad is of shape (F, N)
                    #c_grad_area and c_grad_ar are of shape (N,)
                    gradients["coefficients"][parameter] = c_grad @ param_grad #Shape (F,)
                    gradients["area"][parameter] = c_grad_area @ param_grad
                    gradients["aspect_ratio"][parameter] = c_grad_ar @ param_grad

                for parameter, param_grad in wing.twist_gradient().items():
                    # param_grad is of shape (N,).
                    # a_geo_grad is of shape (F, N)
                    gradients["coefficients"][parameter] = a_geo_grad @ param_grad  # Shape (F,)
            else:
                gradients = None

            yield LiftingLineSolution(wing, self.n_list, coefficients, gradients)