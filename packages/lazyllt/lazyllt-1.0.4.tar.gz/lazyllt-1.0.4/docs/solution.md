# Using a Lifting Line Solution
An instance of the `LiftingLineSolution` class are (lazily) returned by the `LiftingLineModel.solve` method
for each wing in the analysis. `LiftingLineSolution` allows you to access several aerodynamic properties of a wing
and their gradients. Some methods and attributes are marked with `@requires_gradient` and are only available if
`LiftingLineModel.solve` was called with `calculate_gradients=True`.

Note that `LiftingLineSolution` caches all calculated aerodynamic properties and
its attributes are intended to be immutable. To reanalyze a wing, you must use the `LiftingLineModel` class again.

## Aerodynamic properties
Several aerodynamic properties are available as attributes of `LiftingLineSolution`. The analyzed wing can 
also be accessed as `LiftingLineSolution.wing`.

- `LiftingLineSolution.cl` is the lift coefficient of the wing $C_L$.
- `LiftingLineSolution.cdi` is the induced drag coefficient of the wing $C_{D,i}$.
  Note that this does not take into account frictional/pressure drag, which is a property of the airfoil.
- `LiftingLineSolution.cl_slope` is the partial derivative of $C_L$ with respect to the angle of attack $\alpha$.
  Its units are $\text{rad}^{-1}$. This property requires gradients to be loaded.
- `LiftingLineSolution.efficiency` is the Oswald efficiency factor $e$, which ranges between $0$ and $1$, where
  an ideal (elliptical) lift distribution has $e=1$.
- `LiftingLineSolution.alpha_induced` returns the distribution of the induced angle of attack $a_i$.
  Its units are in degrees.
- `LiftingLineSolution.alpha_effective` returns the distribution of the induced angle of attack $a_i$.
  Its units are in degrees.

## Calculation methods
Some aerodynamic properties require extra information about flight conditions to be calculated.
Hence, they are methods instead of attributes.

- `LiftingLineSolution.circulation(v_infty)` returns the circulation distribution along the wing in $\text{m}^2/\text{s}$.
  `v_infty` is the freestream velocity $V_\infty$, in $\text{m}/\text{s}$.
- `LiftingLineSolution.lift(rho, v_infty)` returns the total lift force on the wing in Newtons.
  `rho` is the air density $\rho$, in $\text{kg}/\text{m}^3$.
  `v_infty` is the freestream velocity $V_\infty$, in $\text{m}/\text{s}$.
- `LiftingLineSolution.induced_drag(rho, v_infty)` returns the total induced drag force on the wing in Newtons.
  `rho` is the air density $\rho$, in $\text{kg}/\text{m}^3$.
  `v_infty` is the freestream velocity $V_\infty$, in $\text{m}/\text{s}$.

## Gradients
If `LiftingLineMode.solve` is called with `calculate_gradients=True`, an instance of `LiftingLineSolution` will have
an attribute named `gradients`. `LiftingLineSolution.gradients` is a dictionary such that
$\texttt{gradients["a"]["b"]}=\partial a / \partial b$. By default, gradients can only be calculated for
the Fourier coefficients, wing area, and wing aspect ratio. To find gradients for aerodynamic properties, you must use the:
```python
calculate_gradients(properties, design_variables)
```
method. `properties` is a list of aerodynamic properties and `design_variables` is a list of design variables.
When this method is run, it populates the `LiftingLineSolution.gradients` attribute with the newly calculated gradients.
At the moment, this method can only differentiate scalar properties and not distributions.

The full list of all differentiable wing properties is stored in `LiftingLineSolution.differentiable_properties`
and a full list of design variables which can be differentiated with respect to in `LiftingLineSolution.design_variables`.

## Quantifying solver fit
The pseudo-inverse solver is usually accurate, but very high wing discretizations can cause numerical issues.
The error in the solver's fit can be accessed with `LiftingLineSolution.solver_error`, where:
$$\texttt{solver_error}=\sqrt{\frac{\sum (\alpha_\text{eff}+\alpha_i-\alpha_\text{geo})^2}{N}}$$
in degrees. In other words, it is the root-mean-squared error in calculating the induced angle of attack.
A `LiftingLineSolution` instance will automatically raise a warning on creation if this error is greater than $0.1$.

An important note to consider is that the solver error quantifies how well the solver was able to calculate
Fourier coefficients given the provided wing discretization, **not the actual accuracy of the calculated
aerodynamic properties**. For example, a wing discretized using only 4 nodes may have a very low solver error while
still poorly modeling a real-life scenario.

Receiving maximum modeling accuracy involves maximizing the amount of discretization nodes and Fourier coefficients
while keeping solver error under an acceptable amount.