from typing import Dict, Literal, Any, List

import jax
import jax.numpy as jnp
from functools import cached_property
import warnings
from .wing import UnsweptWing
from .util import aerodynamic_calculator as calc
from .util.fourier_solver import a_i_rms_error

def requires_gradient(func):
    def wrapper(self, *args, **kwargs):
        if self.gradients is None:
            raise ValueError("Called a method which requires gradients, but the gradients were not loaded. Try setting calculate_gradients=True in LiftingLineModel.solve.")
        else:
            return func(self, *args, **kwargs)

    return wrapper

class LiftingLineSolution:
    wing: UnsweptWing

    def __init__(self, wing: UnsweptWing, n_list, coefficients, gradients):
        """
        Solution class for a lifting-line calculation. This class should only be initialized by LiftingLineModel, never
        by the user.
        :param wing: The wing the solution was calculated for.
        :param n_list: List of Fourier coefficient indices. Shape (F,)
        :param coefficients: Fourier coefficients. Shape (F,)
        :param gradients: A dictionary holding named parameters and the
        gradient of the Fourier coefficients wrt the parameter, held in an array of shape (F,).
        """
        self.wing = wing
        self.n_list = n_list
        self.coefficients = coefficients
        self.gradients = gradients

        if gradients:
            #Mapping of strings to properties for gradient information.
            #callable is the jacobian function.
            #parameters is the values that the function is differentiated wrt
            #dependencies is the gradients that need to be calculated (within function_mappings) first
            self.function_mappings: Dict[str, Dict[Literal["callable", "parameters", "dependencies"], Any]] = {
                "cl": {
                    "callable": lambda: jax.jacrev(calc.cl, argnums=(0, 1))(self.coefficients, self.wing.aspect_ratio),
                    "parameters": ["coefficients", "aspect_ratio"],
                    "dependencies": []
                },
                "efficiency": {
                    "callable": lambda: jax.jacrev(calc.efficiency, argnums=(1,))(self.n_list, self.coefficients),
                    "parameters": ["coefficients"],
                    "dependencies": []
                },
                "cdi": {
                    "callable": lambda: jax.jacrev(calc.cdi, argnums=(0, 1, 2))(self.cl, self.efficiency, self.wing.aspect_ratio),
                    "parameters": ["cl", "efficiency", "aspect_ratio"],
                    "dependencies": ["cl", "efficiency"]
                },
                "lift": {
                    "callable": lambda: jax.jacrev(calc.lift, argnums=(0, 1))(self.cl, self.wing.wing_area, 1.0, 1.0),
                    "parameters": ["cl", "area"],
                    "dependencies": ["cl"]
                },
                "induced_drag": {
                    "callable": lambda: jax.jacrev(calc.induced_drag, argnums=(0, 1))(self.cdi, self.wing.wing_area, 1.0, 1.0),
                    "parameters": ["cdi", "area"],
                    "dependencies": ["cdi"]
                }
            }

        error = self.solver_error
        if error > 0.1:
            warnings.warn(f"The solver had an induced angle-or-attack RMS error of {error:.5f} degrees, "
                          "indicating possible numerical issues. You may have an excessively high value for "
                          "num_points and/or num_coefficients.")

    @cached_property
    def solver_error(self):
        """
        The RMS error in calculating the induced angle of attack in degrees.
        A useful metric for detecting silent numerical issues.
        Note that this metric shows how well the solver fit the solution given the provided constraints,
        not the accuracy of the aerodynamic properties.
        """
        return jnp.rad2deg(a_i_rms_error(
            self.n_list,
            self.coefficients,
            self.wing.thetas,
            self.wing.c,
            self.wing.alpha_geo,
            self.wing.b,
            self.wing.alpha_0
        ))

    @cached_property
    @requires_gradient
    def design_variables(self):
        """
        A list of design variables that a wing property can be differentiated with respect to.
        Requires gradients to be loaded.
        """
        return set(self.gradients["coefficients"].keys())

    @cached_property
    @requires_gradient
    def differentiable_properties(self):
        """
        A list of differentiable properties of the wing.
        Requires gradients to be loaded.
        """
        #Both loaded and unloaded properties
        return set(self.function_mappings.keys() | self.gradients.keys())

    @requires_gradient
    def calculate_gradients(self, properties: List[str], design_variables: List[str]):
        """
        Calculates the gradients of a list of wing properties with respect to a list of design variables.
        Populates the calculated gradients in the ``gradients`` attribute.
        Requires gradients to be loaded. Note that all gradients are calculated in MKS+degrees.
        :param properties: A list of wing properties
        :param design_variables: A list of design variables
        :return: The dictionary of all calculated gradients.
        """

        for prop in properties:
            if prop not in self.differentiable_properties:
                warnings.warn(f"{prop} is not a differentiable wing property; skipped.")
                continue

            # Create dictionary for derivatives if not existing
            self.gradients[prop] = self.gradients.get(prop, dict())

            mapping = self.function_mappings[prop]

            #Calculate the partials of all the dependency functions
            dependencies = mapping["dependencies"]
            if len(dependencies) > 0:
                self.calculate_gradients(dependencies, design_variables)

            #Calculate the jacobian wrt the parameters of the function and populate the gradients dict
            jacobian = mapping["callable"]()
            for param, grad in zip(mapping["parameters"], jacobian):
                self.gradients[prop][param] = grad

            for dv in design_variables:
                if dv not in self.design_variables:
                    warnings.warn(f"{dv} is not a valid design variable; skipped.")
                    continue

                # Do not recalculate if the gradient is already there
                if self.gradients[prop].get(dv) is not None:
                    continue

                total_grad = jnp.float32(0)
                for param in mapping["parameters"]:
                    #Only calculate the partial if it exists
                    base_grad = self.gradients[param].get(dv)
                    if base_grad is not None:
                        total_grad += jnp.dot(base_grad, self.gradients[prop][param])
                self.gradients[prop][dv] = total_grad

        return self.gradients

    @cached_property
    def cl(self):
        """
        Wing coefficient of lift.
        """
        return calc.cl(self.coefficients, self.wing.aspect_ratio)


    @cached_property
    @requires_gradient
    def cl_slope(self):
        """
        Helper attribute to get slope of the wing coefficient of lift w.r.t. angle of attack in radians.
        """
        self.calculate_gradients(["cl"], ["aoa"])

        #Since the slope gradient is in units deg^-1, it must be divided by the deg2rad factor
        return jnp.rad2deg(self.gradients["cl"]["aoa"])

    @cached_property
    def cdi(self):
        """
        Coefficient of induced drag.
        """
        return calc.cdi(self.cl, self.efficiency, self.wing.aspect_ratio)

    @cached_property
    def efficiency(self):
        """
        Oswald efficiency factor.
        """
        return calc.efficiency(self.n_list, self.coefficients)

    def lift(self, rho, v_infty):
        """
        :param rho: Air density in kg/m^3.
        :param v_infty: Freestream velocity in m/s.
        :return: The lift force in newtons.
        """
        return calc.lift(self.cl, self.wing.wing_area, rho, v_infty)

    def induced_drag(self, rho, v_infty):
        """
        :param rho: Air density in kg/m^3.
        :param v_infty: Freestream velocity in m/s.
        :return: The induced drag force in newtons.
        """
        return calc.induced_drag(self.cdi, self.wing.wing_area, rho, v_infty)

    def circulation(self, v_infty):
        """
        Gets the circulation distribution of the wing. The distribution is evenly spaced.
        :param v_infty: The freestream velocity in m/s.
        :return: Circulation distribution in m^2/s. Shape (N,)
        """

        return 2 * self.wing.b * v_infty * calc.unitless_circulation(self.n_list, self.wing.thetas, self.coefficients)

    @cached_property
    def alpha_induced(self):
        """
        The induced angle of attack distribution in degrees. Shape (N,)
        """
        return jnp.rad2deg(calc.alpha_induced(self.n_list, self.wing.thetas, self.coefficients))

    @cached_property
    def alpha_effective(self):
        """
        The effective angle of attack distribution in degrees.
        """
        return jnp.rad2deg(self.wing.alpha_geo) - self.alpha_induced #Shape (N,)