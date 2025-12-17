# Running a Lifting Line Analysis
Once you have defined a wing, you can run a Lifting-Line analysis on it using the `LiftingLineModel` class.

## Defining the model

A lifting-line model can be defined using the `LiftingLineModel` class:

```python
LiftingLineModel(
    num_coefficients: int = 35
)
```

where `num_coefficients` is the number of Fourier coefficients used to find the solution. More coefficients leads to
a more accurate solution at the cost of solver performance.

## Adding wings to a model
Once you have defined a model, you must add wings for it to analyze. This is done using the:
```python
add_wing(wing: UnsweptWing)
```
method. You can call this method several times to add multiple wings,
which can be useful for use-cases like genetic optimization.

## Running the solver
You can run the solver by using the:
```python
solve(calculate_gradients: bool = False)
```
method. This method returns an iterator which lazily calculates each wing's solution
and returns `LiftingLineSolution` objects as it is looped over. When `calculate_gradients` is set to true,
each `LiftingLineSolution` class will be able to calculate gradients.