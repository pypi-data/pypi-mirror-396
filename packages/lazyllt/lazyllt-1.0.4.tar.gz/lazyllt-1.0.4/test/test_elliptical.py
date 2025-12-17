import unittest
from lazyllt import LiftingLineModel, UnsweptWing
import jax.numpy as jnp


# Test that the solver works with an elliptical distribution.
class TestElliptical(unittest.TestCase):
    #Make sure that the Oswald efficiency factor for an elliptically loaded wing is close to 1.
    def test_efficiency(self):
        model = LiftingLineModel()
        wing = UnsweptWing(
            span=5,
            root_chord=1,
            alpha_0=-1
        )
        wing.set_taper_function(lambda z, _: jnp.sqrt(1 - z ** 2))
        wing.parametric_taper()

        model.add_wing(wing)
        solution = next(model.solve())

        self.assertAlmostEqual(solution.efficiency, 1, places=4)

    #Test that the lift slope is theoretically correct for an elliptically loaded wing.
    def test_lift_slope(self):
        model = LiftingLineModel()
        wing = UnsweptWing(
            span=5,
            root_chord=1,
            alpha_0=-1
        )
        wing.set_taper_function(lambda z, _: jnp.sqrt(1 - z ** 2))
        wing.parametric_taper()

        model.add_wing(wing)
        solution = next(model.solve(calculate_gradients=True))
        slope = solution.cl_slope
        theoretical_slope = 2 * jnp.pi / (1 + 2 / wing.aspect_ratio)

        self.assertAlmostEqual(slope, theoretical_slope, places=2)

    #Test that the integrated circulation matches the total lift within 1%
    def test_circulation(self):
        model = LiftingLineModel()
        wing = UnsweptWing(
            span=5,
            root_chord=1,
            alpha_0=-1
        )
        wing.set_taper_function(lambda z, _: jnp.sqrt(1 - z ** 2))
        wing.parametric_taper()

        model.add_wing(wing)
        solution = next(model.solve(calculate_gradients=True))

        v_infty = 100
        rho = 1
        l_prime = rho * v_infty * solution.circulation(v_infty)
        lift = jnp.trapezoid(l_prime, wing.nodes).item()

        self.assertAlmostEqual(lift, solution.lift(rho, v_infty), delta=lift/100)

if __name__ == "__main__":
    unittest.main()