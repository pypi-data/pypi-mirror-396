<a id="lazyllt.solution"></a>

# lazyllt.solution

<a id="lazyllt.solution.LiftingLineSolution"></a>

## LiftingLineSolution Objects

```python
class LiftingLineSolution()
```

<a id="lazyllt.solution.LiftingLineSolution.__init__"></a>

#### \_\_init\_\_

```python
def __init__(wing: UnsweptWing, n_list, coefficients, gradients)
```

Solution class for a lifting-line calculation. This class should only be initialized by LiftingLineModel, never

by the user.

**Arguments**:

- `wing`: The wing the solution was calculated for.
- `n_list`: List of Fourier coefficient indices. Shape (F,)
- `coefficients`: Fourier coefficients. Shape (F,)
- `gradients`: A dictionary holding named parameters and the
gradient of the Fourier coefficients wrt the parameter, held in an array of shape (F,).

<a id="lazyllt.solution.LiftingLineSolution.solver_error"></a>

#### solver\_error

```python
@cached_property
def solver_error()
```

The RMS error in calculating the induced angle of attack in degrees.
A useful metric for detecting silent numerical issues.
Note that this metric shows how well the solver fit the solution given the provided constraints,
not the accuracy of the aerodynamic properties.

<a id="lazyllt.solution.LiftingLineSolution.design_variables"></a>

#### design\_variables

```python
@cached_property
@requires_gradient
def design_variables()
```

A list of design variables that a wing property can be differentiated with respect to.
Requires gradients to be loaded.

<a id="lazyllt.solution.LiftingLineSolution.differentiable_properties"></a>

#### differentiable\_properties

```python
@cached_property
@requires_gradient
def differentiable_properties()
```

A list of differentiable properties of the wing.
Requires gradients to be loaded.

<a id="lazyllt.solution.LiftingLineSolution.calculate_gradients"></a>

#### calculate\_gradients

```python
@requires_gradient
def calculate_gradients(properties: List[str], design_variables: List[str])
```

Calculates the gradients of a list of wing properties with respect to a list of design variables.

Populates the calculated gradients in the ``gradients`` attribute.
Requires gradients to be loaded. Note that all gradients are calculated in MKS+degrees.

**Arguments**:

- `properties`: A list of wing properties
- `design_variables`: A list of design variables

**Returns**:

The dictionary of all calculated gradients.

<a id="lazyllt.solution.LiftingLineSolution.cl"></a>

#### cl

```python
@cached_property
def cl()
```

Wing coefficient of lift.

<a id="lazyllt.solution.LiftingLineSolution.cl_slope"></a>

#### cl\_slope

```python
@cached_property
@requires_gradient
def cl_slope()
```

Helper attribute to get slope of the wing coefficient of lift w.r.t. angle of attack in radians.

<a id="lazyllt.solution.LiftingLineSolution.cdi"></a>

#### cdi

```python
@cached_property
def cdi()
```

Coefficient of induced drag.

<a id="lazyllt.solution.LiftingLineSolution.efficiency"></a>

#### efficiency

```python
@cached_property
def efficiency()
```

Oswald efficiency factor.

<a id="lazyllt.solution.LiftingLineSolution.lift"></a>

#### lift

```python
def lift(rho, v_infty)
```

**Arguments**:

- `rho`: Air density in kg/m^3.
- `v_infty`: Freestream velocity in m/s.

**Returns**:

The lift force in newtons.

<a id="lazyllt.solution.LiftingLineSolution.induced_drag"></a>

#### induced\_drag

```python
def induced_drag(rho, v_infty)
```

**Arguments**:

- `rho`: Air density in kg/m^3.
- `v_infty`: Freestream velocity in m/s.

**Returns**:

The induced drag force in newtons.

<a id="lazyllt.solution.LiftingLineSolution.circulation"></a>

#### circulation

```python
def circulation(v_infty)
```

Gets the circulation distribution of the wing. The distribution is evenly spaced.

**Arguments**:

- `v_infty`: The freestream velocity in m/s.

**Returns**:

Circulation distribution in m^2/s. Shape (N,)

<a id="lazyllt.solution.LiftingLineSolution.alpha_induced"></a>

#### alpha\_induced

```python
@cached_property
def alpha_induced()
```

The induced angle of attack distribution in degrees. Shape (N,)

<a id="lazyllt.solution.LiftingLineSolution.alpha_effective"></a>

#### alpha\_effective

```python
@cached_property
def alpha_effective()
```

The effective angle of attack distribution in degrees.

<a id="lazyllt.model"></a>

# lazyllt.model

<a id="lazyllt.model.LiftingLineModel"></a>

## LiftingLineModel Objects

```python
class LiftingLineModel()
```

<a id="lazyllt.model.LiftingLineModel.__init__"></a>

#### \_\_init\_\_

```python
def __init__(num_coefficients: int = 35)
```

A class used to manage the lifting-line problem.

**Arguments**:

- `num_coefficients`: The number of Fourier coefficients to use in the solver. Must be at least 1.

<a id="lazyllt.model.LiftingLineModel.solve"></a>

#### solve

```python
def solve(
        calculate_gradients=False
) -> Generator[LiftingLineSolution, None, None]
```

Lazily calculates the lifting-line solution for each of the given wings.

Throws an error if no wings have been added to the model.

**Arguments**:

- `calculate_gradients`: Whether to calculate gradients or not. Disabled by default, useful for optimization.

**Returns**:

A generator yielding LiftingLineSolution(s).

<a id="lazyllt.wing"></a>

# lazyllt.wing

<a id="lazyllt.wing.UnsweptWing"></a>

## UnsweptWing Objects

```python
class UnsweptWing()
```

<a id="lazyllt.wing.UnsweptWing.__init__"></a>

#### \_\_init\_\_

```python
def __init__(span: float,
             root_chord: float,
             alpha_0: float,
             aoa: float = 0.0,
             num_points: int = 50)
```

A wing without sweep or dihedral.

By default, a rectangular wing with no twist.

**Arguments**:

- `span`: The wingspan in meters.
- `root_chord`: The length of the chord at the wing root, in meters.
- `alpha_0`: The zero-lift angle of the wing, in degrees. This is a property of the airfoil geometry.
- `aoa`: The angle of attack of the wing, in degrees.
- `num_points`: The number of points used to discretize the wing. Must be at least 4.

<a id="lazyllt.wing.UnsweptWing.set_taper_function"></a>

#### set\_taper\_function

```python
def set_taper_function(f: Callable[[Array, Dict[str, float]], Array])
```

Set a custom parametric chord distribution function.

**Arguments**:

- `f`: A function(z, t)->c such that 0 <= z_i <= 1 and 0 < c_i <= 1.
z_i=0 is the wing base and z_i=1 is either wing tip. t is a dictionary of named parameters.
c_i is a fraction of the root chord length.

<a id="lazyllt.wing.UnsweptWing.parametric_taper"></a>

#### parametric\_taper

```python
def parametric_taper(parameters: Optional[Dict[str, float]] = None)
```

Evaluate the currently set parametric chord distribution function.

**Arguments**:

- `parameters`: A dictionary of named parameters.

<a id="lazyllt.wing.UnsweptWing.linear_taper"></a>

#### linear\_taper

```python
def linear_taper(taper_ratio)
```

Sets a linearly tapered chord distribution.

**Arguments**:

- `taper_ratio`: The ratio between the length of the tip chord and root chord. Must be between 0 and 1.

<a id="lazyllt.wing.UnsweptWing.taper_gradient"></a>

#### taper\_gradient

```python
def taper_gradient()
```

Returns the partial derivative of the wing chord distribution with respect to the taper parameters.

**Returns**:

A dictionary mapping named parameters to a gradient array of shape (N,).

<a id="lazyllt.wing.UnsweptWing.set_twist_function"></a>

#### set\_twist\_function

```python
def set_twist_function(f: Callable[[Array, Dict[str, float]], Array])
```

Set a custom parametric chord distribution function.

**Arguments**:

- `f`: A function(z, t)->a such that 0 <= z_i <= 1.
z_i=0 is the wing base and z_i=1 is either wing tip. t is a dictionary of named parameters.
a_i is the twist angle at a point in degrees.

<a id="lazyllt.wing.UnsweptWing.parametric_twist"></a>

#### parametric\_twist

```python
def parametric_twist(parameters: Optional[Dict[str, float]] = None)
```

Evaluate the currently set parametric twist distribution function.

**Arguments**:

- `parameters`: A dictionary of named parameters.

<a id="lazyllt.wing.UnsweptWing.linear_twist"></a>

#### linear\_twist

```python
def linear_twist(root_twist: float, tip_twist: float)
```

Sets a linear twist distribution.

**Arguments**:

- `root_twist`: Twist at the wing root, in degrees.
- `tip_twist`: Twist at the wing tip, in degrees.

<a id="lazyllt.wing.UnsweptWing.twist_gradient"></a>

#### twist\_gradient

```python
def twist_gradient()
```

Returns the partial derivative of the wing twist distribution with respect to the twist parameters.

**Returns**:

A dictionary mapping named parameters to a gradient array of shape (N,).

<a id="lazyllt.util.fourier_solver"></a>

# lazyllt.util.fourier\_solver

<a id="lazyllt.util.fourier_solver.solve_coefficients"></a>

#### solve\_coefficients

```python
@jax.jit
def solve_coefficients(n_list, thetas, c, alpha_geo, b, alpha_0)
```

Solve for the Fourier coefficients using matrix pseudo-inverses.

**Arguments**:

- `n_list`: Shape (F,)
- `thetas`: Shape (N,)
- `c`: Shape (N,)
- `alpha_geo`: Shape (N,). In radians.
- `b`: Scalar.
- `alpha_0`: Scalar. In radians.

**Returns**:

Shape (F,)

<a id="lazyllt.util.fourier_solver.a_i_rms_error"></a>

#### a\_i\_rms\_error

```python
@jax.jit
def a_i_rms_error(n_list, coefficients, thetas, c, alpha_geo, b, alpha_0)
```

Get the RMS error in induced angle of attack (in radians) given calculated coefficients.

**Arguments**:

- `n_list`: Shape (F,)
- `coefficients`: Shape (F,)
- `thetas`: Shape (N,)
- `c`: Shape (N,)
- `alpha_geo`: Shape (N,). In radians.
- `b`: Scalar.
- `alpha_0`: Scalar. In radians.

**Returns**:

Shape (F,)

<a id="lazyllt.util"></a>

# lazyllt.util

Utility methods; not user-facing.

<a id="lazyllt.util.aerodynamic_calculator"></a>

# lazyllt.util.aerodynamic\_calculator

A collection of pure functions used to calculate wing properties.

