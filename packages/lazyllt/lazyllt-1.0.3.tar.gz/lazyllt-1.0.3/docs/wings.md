# Wings
A wing can be defined using the `UnsweptWing` class.
Swept wings are currently not supported due to the limitations of classical lifting-line theory.

## Creating a wing
A wing can be defined using the `UnsweptWing` constructor:

```python
UnsweptWing(
    span: float,
    root_chord: float,
    alpha_0: float,
    aoa: float = 0.0,
    num_points: int = 50
)
```
- `span` is the tip-to-tip wingspan in meters. Must be a positive number.
- `root_chord` is the length of the chord at the wing root, in meters. Must be a positive number.
- `alpha_0` is the angle of attack at which the wing's airfoil generates zero lift, in degrees.
  This is usually a negative number unless you are dealing with an abnormal airfoil shape.
- `aoa` is the angle of attack of the wing, in degrees.
- `num_points` is the number of nodes to use when discretizing the wing during calculations.
  A higher value can increase solver accuracy at the cost of some performance.
  Very high values can also cause numerical issues. Must be greater than 4.

## Linear taper
A classic tapered wing can be created by calling the:
```python 
linear_taper(taper_ratio: float)
```
method on
an `UnsweptWing` object, where $0<\texttt{taper_ratio}\leq 1$. This modifies the chord distribution in-place.

## Linear twist distribution
Similarly, a linear twist distribution (often used for washout or incidence) can be created by calling the:
```python
linear_twist(root_twist: float, tip_twist: float)
```
method. `root_twist` is the angle at the wing root
and `tip_twist` is the angle at either wing tip. Both angles are in degrees.
Note that, when the wing's angle of attack is not 0, `root_twist` and `chord_twist` are relative to the
airplane's longitudinal axis rather than the freestream.

## Custom chord distributions
A custom chord distribution can be created by calling the:
```python
set_taper_function(f: Callable[[Array, Dict[str, float]], Array])
```
method. `f` is a function with the signature $f(z,\texttt{params})\to c$.
- $z$ is a JAX array of shape $(N,)$
where $N$ is the value of `num_points`. The $i$th point in $z$ represents the $i$th wing point,
where $0\leq z_i \leq 1$. At the wing root, $z_i=0$ and at either wing tip, $z_i=1$.
- $\texttt{params}$ is a dictionary of numeric parameters that can be used for parametric distributions.
- $c$ is a JAX array of shape $(N,)$. $c_i$ is the chord length of the wing at $z_i$ as a multiple of the root chord.
  For most chord distributions, $0 < c_i\leq 1$.

After defining the chord distribution, you must call the:
```python
parametric_taper(parameters: Optional[Dict[str, float]])
```
method. `parameters` is the parameters that are passed to your defined $f$ function. Note that
`parametric_taper` must be called even if $f$ is not parametric;
otherwise, the chord distribution will not be affected.

### Example

```python
from lazyllt import UnsweptWing

wing = UnsweptWing(
    # [...]
)


def elliptical(z, params):
    return (1 - params["a"] * z ** 2) ** 0.5


wing.set_taper_function(elliptical)
wing.parametric_taper({"a": 0.85})
```

## Custom twist distributions
A custom twist distribution can be created by calling the:
```python
set_twist_function(f: Callable[[Array, Dict[str, float]], Array])
```
method. `f` is a function with the signature $f(z, \texttt{params})\to \alpha$.
- $z$ and $\texttt{params}$ have the same meaning as for `set_taper_function`.
- $\alpha$ is a JAX array of shape $(N,)$. $\alpha_i$ is the angle of attack relative to the airplane's
  longitudinal axis at $z_i$.

Similar to a custom chord distribution, you must call the:
```python
parametric_twist(parameters: Optional[Dict[str, float]])
```
method to apply your custom twist distribution.

### Example

```python
import jax.numpy as jnp
from lazyllt import UnsweptWing

wing = UnsweptWing(
    # [...]
)


def linear(z, params):
    return -params["a"] * jnp.abs(z) + 1


wing.set_taper_function(linear)
wing.parametric_taper({"a": 1.5})
```
