import warnings
from typing import Callable, Dict, Optional

import jax
import jax.numpy as jnp
from jaxtyping import Array
from .util import aerodynamic_calculator as calc


class UnsweptWing:
    #Scalar properties
    num_points: int
    b: float
    alpha_0: float
    root_chord: float

    #Array properties
    thetas: Array
    c: Array
    alpha_geo: Array

    taper_fn: Callable[[Array, Dict], Array]
    taper_params: Dict
    twist_fn: Callable[[Array, Dict], Array]
    twist_params: Dict

    #Computed properties
    @property
    def wing_area(self):
        return calc.wing_area_ar(self.thetas, self.b, self.c)[0]

    @property
    def aspect_ratio(self):
        return calc.wing_area_ar(self.thetas, self.b, self.c)[1]

    @property
    def nodes(self):
        return -0.5 * self.b * jnp.cos(self.thetas)

    def __init__(self, span: float, root_chord: float, alpha_0: float, aoa: float=0.0, num_points: int = 50):
        """
        A wing without sweep or dihedral.
        By default, a rectangular wing with no twist.
        :param span: The wingspan in meters.
        :param root_chord: The length of the chord at the wing root, in meters.
        :param alpha_0: The zero-lift angle of the wing, in degrees. This is a property of the airfoil geometry.
        :param aoa: The angle of attack of the wing, in degrees.
        :param num_points: The number of points used to discretize the wing. Must be at least 4.
        """
        if num_points < 4:
            raise ValueError(f"num_points must be at least 4; got {num_points}.")
        if span <= 0:
            raise ValueError(f"span must be greater than 0; got {span}.")
        if root_chord <= 0:
            raise ValueError(f"root_chord must be greater than 0; got {root_chord}.")
        if alpha_0 > 0:
            warnings.warn(f"Expected a nonpositive value for alpha_0; got {alpha_0}. This may be a mistake, because "
                          "it implies the airfoil generates negative lift at zero angle of attack.")
        if num_points > 1000:
            warnings.warn(f"num_points values of over 1000 can cause silent numerical issues; got {num_points}.")

        self.num_points = num_points
        self.thetas = jnp.linspace(1e-3, jnp.pi - 1e-3, num_points) #Shape (N,)

        self.root_chord = jnp.float32(root_chord)
        self.c = jnp.full((num_points,), self.root_chord) #Shape (N,)
        self.b = jnp.float32(span)

        self.aoa = jnp.deg2rad(aoa)
        self.alpha_geo = jnp.zeros_like(self.thetas) + self.aoa #Shape (N,)
        self.alpha_0 = jnp.deg2rad(alpha_0).item()

        self.taper_fn = lambda z, t: self.c
        self.taper_params = dict()
        self.twist_fn = lambda z, t: self.alpha_geo
        self.twist_params = dict()

    def __str__(self):
        return f"""
Wing {{
    span = {self.b} m
    root_chord = {self.root_chord} m
    alpha_0 = {jnp.rad2deg(self.alpha_0).item():.5f} deg
    aoa = {jnp.rad2deg(self.aoa).item():.5f} deg
    taper_params = {self.taper_params}
    twist_params = {self.twist_params}
    num_points = {self.num_points}
}}"""

    def __repr__(self):
        return self.__str__()

    def set_taper_function(self, f: Callable[[Array, Dict[str, float]], Array]):
        """
        Set a custom parametric chord distribution function.
        :param f: A function(z, t)->c such that 0 <= z_i <= 1 and 0 < c_i <= 1.
            z_i=0 is the wing base and z_i=1 is either wing tip. t is a dictionary of named parameters.
            c_i is a fraction of the root chord length.
        :return:
        """
        self.taper_fn = f

    def parametric_taper(self, parameters: Optional[Dict[str, float]] = None):
        """
        Evaluate the currently set parametric chord distribution function.
        :param parameters: A dictionary of named parameters.
        :return:
        """
        if parameters is None:
            parameters = dict()

        # Make z go from 1 to 0 to 1 for easier scaling
        z = jnp.abs(-jnp.cos(self.thetas))

        self.taper_params = parameters
        self.c = jnp.float32(self.root_chord) * self.taper_fn(z, parameters)

    def linear_taper(self, taper_ratio):
        """
        Sets a linearly tapered chord distribution.
        :param taper_ratio: The ratio between the length of the tip chord and root chord. Must be between 0 and 1.
        :return:
        """
        if taper_ratio <= 0 or taper_ratio > 1:
            raise ValueError(f"taper_ratio must be between 0 and 1; got {taper_ratio}.")


        def f(z, params):
            ratio = params["taper_ratio"]
            c = 1 - (1 - ratio) * z

            return c

        self.set_taper_function(f)
        self.parametric_taper({"taper_ratio": jnp.float32(taper_ratio)})

    def taper_gradient(self):
        """
        Returns the partial derivative of the wing chord distribution with respect to the taper parameters.
        :return: A dictionary mapping named parameters to a gradient array of shape (N,).
        """
        # Make z go from 1 to 0 to 1 for easier scaling
        z = jnp.abs(-jnp.cos(self.thetas))

        if self.taper_params and len(self.taper_params) > 0:
            gradients: Dict = jax.jacrev(self.taper_fn, argnums=1)(z, self.taper_params)
        else:
            gradients = dict()

        #The gradients need to be scaled based on the root chord
        for param in gradients.keys():
            gradients[param] *= self.root_chord

        #Since the root chord is a scaling variable, its gradient is just the unscaled chord distribution
        gradients["root_chord"] = self.taper_fn(z, self.taper_params)

        return gradients

    def set_twist_function(self, f: Callable[[Array, Dict[str, float]], Array]):
        """
        Set a custom parametric chord distribution function.
        :param f: A function(z, t)->a such that 0 <= z_i <= 1.
            z_i=0 is the wing base and z_i=1 is either wing tip. t is a dictionary of named parameters.
            a_i is the twist angle at a point in degrees.
        :return:
        """
        self.twist_fn = f

    def parametric_twist(self, parameters: Optional[Dict[str, float]] = None):
        """
        Evaluate the currently set parametric twist distribution function.
        :param parameters: A dictionary of named parameters.
        :return:
        """
        if parameters is None:
            parameters = dict()

        # Make z go from 1 to 0 to 1 for easier scaling
        z = jnp.abs(-jnp.cos(self.thetas))

        self.twist_params = parameters
        self.alpha_geo = jnp.deg2rad(self.twist_fn(z, parameters)) + self.aoa

    def linear_twist(self, root_twist: float, tip_twist: float):
        """
        Sets a linear twist distribution.
        :param root_twist: Twist at the wing root, in degrees.
        :param tip_twist: Twist at the wing tip, in degrees.
        :return:
        """

        def f(z, params):
            root = params["root_twist"]
            tip = params["tip_twist"]

            return root_twist + (root - tip) * z


        self.set_twist_function(f)
        self.parametric_twist({
            "root_twist": jnp.deg2rad(root_twist).item(),
            "tip_twist": jnp.deg2rad(tip_twist).item()
        })


    def twist_gradient(self):
        """
        Returns the partial derivative of the wing twist distribution with respect to the twist parameters.
        :return: A dictionary mapping named parameters to a gradient array of shape (N,).
        """
        # Make z go from 1 to 0 to 1 for easier scaling
        z = jnp.abs(-jnp.cos(self.thetas))

        if self.twist_params and len(self.twist_params) > 0:
            gradients: Dict = jax.jacrev(self.twist_fn, argnums=1)(z, self.twist_params)
        else:
            gradients = dict()

        #Since the angle of attack just adds on to the current angle, its gradient is just 1 degree per degree.
        gradients["aoa"] = jnp.ones_like(z)

        return gradients
