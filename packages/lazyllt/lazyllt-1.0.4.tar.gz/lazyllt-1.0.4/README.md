# LazyLLT: A Lightweight  Lifting-line Analysis Library

LazyLLT is a library for quickly calculating a wing's aerodynamic properties and their respective
gradients using the Lanchester–Prandtl lifting-line theory. When not calculating gradients, LazyLLT can
accurately compute a wing's aerodynamic properties in under a millisecond.

LazyLLT is "lazy" in two ways:
1. An aerodynamic analysis can be done oftentimes in under 10 lines of code.
2. No property or design variable gradient is computed until its value is queried.

For more information, please view the documentation.

## Install

`pip install lazyllt`

Requires Python 3.10 or higher.

## Example
Example of getting the lift coefficient of a wing with an elliptical chord distribution and linear twist (washout):

```python
from lazyllt import LiftingLineModel, UnsweptWing

model = LiftingLineModel(num_coefficients=35)

wing = UnsweptWing(
    span=5,
    root_chord=1,
    alpha_0=-1
)


def elliptical(z, _):
    return (1 - z ** 2) ** 0.5


wing.set_taper_function(elliptical)
wing.parametric_taper()

wing.linear_twist(
    root_twist=1,
    tip_twist=0
)

model.add_wing(wing)
solution = next(model.solve())

print("Coefficient of lift:", solution.cl)
```

## Note on Units
LazyLLT uses the meter-kilogram-second unit system for all physical values and properties.
All user-facing methods and attributes represent angles in degrees unless specified.
Most internal functions and attributes use radians for ease of calculation.