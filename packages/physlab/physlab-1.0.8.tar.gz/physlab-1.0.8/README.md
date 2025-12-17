# PhysLab

Modern Python library for physical quantities with automatic uncertainty propagation

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Quick Start

### Installation
```bash
pip install physlab
```

### Basic Usage
```python
import numpy as np
from physlab import phys, LabProcessor, graph, sin, cos, tg, ctg, exp, ln, log10, sqrt, arcsin, arccos, arctg

# Create physical quantities
length = phys(10.5, 0.1)    # 10.5 ± 0.1 m
time = phys(2.3, 0.05)      # 2.3 ± 0.05 s

# Automatic uncertainty calculation
velocity = length / time
print(f"Velocity: {velocity}")

# Working with arrays
temperatures = phys([20.1, 22.3, 25.7], 0.5)
print(f"Temperatures: {temperatures}")
```

## Core Features

### Physical Quantities with Uncertainties

**Creating Objects:**
```python
# Scalars
scalar = phys(15.7, 0.2)

# Arrays with uniform uncertainty
array_uniform = phys([1, 2, 3, 4], 0.1)

# Arrays with variable uncertainty  
array_variable = phys([1.0, 2.0, 3.0], [0.1, 0.2, 0.3])

# From NumPy arrays
np_array = phys(np.array([0.1, 0.2, 0.3]), 0.01)
```

**Properties and Access:**
```python
x = phys(25.0, 0.5)

# Basic properties
print(f"Value: {x.value}")
print(f"Absolute uncertainty: {x.sigma}")
print(f"Relative uncertainty: {x.eps:.4f}")

# Setting uncertainties
x.sigma = 0.8      # Set absolute uncertainty
x.eps = 0.05       # Set relative uncertainty (5%)

# For arrays
arr = phys([10, 20, 30])
arr.eps = 0.1      # Automatically creates uncertainty array
```

### Mathematical Operations

**Automatic Uncertainty Propagation:**
- Addition/Subtraction: σ = √(σ₁² + σ₂²)
- Multiplication/Division: ε = √(ε₁² + ε₂²)
- Power: Full calculation for base and exponent

```python
a = phys(10.0, 0.1)
b = phys(2.0, 0.05)

print(f"a + b = {a + b}")
print(f"a - b = {a - b}") 
print(f"a * b = {a * b}")
print(f"a / b = {a / b}")
print(f"a ** 2 = {a ** 2}")
print(f"2 ** a = {2 ** a}")

# Operations with numbers
print(f"a + 5 = {a + 5}")
print(f"3 * a = {3 * a}")

# Complex expressions
complex_expr = (a + b) * phys(3, 0.1) / 2
```

### Mathematical Functions

**Supported functions with automatic uncertainty calculation:**

```python
from physlab import cos, sin, tg, ctg, exp, ln, sqrt

angle = phys(0.5, 0.01)  # 0.5 ± 0.01 radians

print(f"cos({angle}) = {cos(angle)}")
print(f"sin({angle}) = {sin(angle)}")
print(f"tg({angle}) = {tg(angle)}")
print(f"ctg({angle}) = {ctg(angle)}")

# Exponential and logarithms
x = phys(2.0, 0.1)
print(f"exp({x}) = {exp(x)}")
print(f"ln({x}) = {ln(x)}")
print(f"sqrt({x}) = {sqrt(x)}")

# Working with arrays
angles_array = phys([0, np.pi/6, np.pi/4, np.pi/3], 0.01)
sines = sin(angles_array)
```

### Array Operations

```python
# Creation and basic operations
data = phys([1.0, 2.0, 3.0, 4.0], 0.1)

# Indexing
print(f"First element: {data[0]}")
print(f"Slice [1:3]: {data[1:3]}")

# Element-wise operations
multiplied = data * phys([2, 2, 2, 2], 0.05)

# Operations with scalars
shifted = data + 10
```

### Scalar-Array Transformations

```python
# Unpacking array into individual quantities
voltages = phys([3.3, 5.0, 12.0], [0.1, 0.1, 0.2])
v1, v2, v3 = voltages

# Combining into array
combined = phys.concatenate([v1, v2, v3])

# Adding elements
measurements = phys(1.5, 0.1)
measurements.append(phys(1.6, 0.1))
measurements.append(phys(1.4, 0.1))
```

### Sorting and Reordering

```python
unsorted = phys([3, 1, 4, 2], [0.3, 0.1, 0.4, 0.2])

# Sorting
sorted_data = unsorted.sort()
print(f"Sort order: {unsorted.sort_order}")

# Using sorted property
print(f"Via sorted property: {unsorted.sorted}")

# Reordering
reordered = unsorted.in_order([2, 0, 3, 1])
```

## Data Analysis with LabProcessor

### Statistical Methods

```python
lab = LabProcessor()

# Weighted mean
measurements = [phys(10.0, 0.1), phys(10.5, 0.2), phys(9.8, 0.15)]
weighted_avg = lab.weighted_mean(measurements)

# Least squares method
x_data = phys([1, 2, 3, 4], 0.1)
y_data = phys([2.1, 3.9, 6.2, 8.1], [0.2, 0.3, 0.25, 0.4])

k, b = lab.weighted_least_squares(x_data, y_data)

# Multiple datasets
x_sets = [phys([1, 2, 3], 0.1), phys([4, 5, 6], 0.1)]
y_sets = [phys([2, 4, 6], 0.2), phys([8, 10, 12], 0.2)]

k_multi, b_multi = lab.weighted_least_squares(x_sets, y_sets)
```

### LaTeX Generation

```python
# Tables
experiment_data = [
    phys(1.234e-6, 0.001e-6),
    phys(2.345e-6, 0.002e-6), 
    phys(3.456e-6, 0.003e-6)
]

table_latex = lab.latex_table(
    experiment_data, 
    header=["Measurement", "Value"], 
    exp=True
)

# Value formatting
resistance = phys(1.234e3, 0.015e3)
value_latex = lab.latex_value(resistance, name="R", exp=True)

# Scientific notation conversion
text_with_exp = "Resistance value 1.23e3 Ω at current 2.5e-2 A"
converted_text = lab.e_to_tex(text_with_exp)
```

## Professional Visualization with Graph

### Basic Usage

```python
# Simple plot with approximation
x = phys([1, 2, 3, 4, 5], 0.1)
y = phys([2.1, 3.9, 6.0, 8.2, 9.8], [0.2, 0.3, 0.25, 0.4, 0.35])

g = graph(x, y, approx=True)
g.xlabel('Time, s')
g.ylabel('Velocity, m/s')
g.add_title('Velocity vs Time')
g.add_params_text()
g.show()
```

### Multiple Data Series

```python
# Multiple experiments with common X
x_common = phys([1, 2, 3, 4, 5], 0.1)

y_experiments = [
    phys([2.1, 3.9, 6.0, 8.2, 9.8], [0.2, 0.3, 0.25, 0.4, 0.35]),
    phys([1.8, 3.7, 5.8, 7.9, 9.5], [0.15, 0.25, 0.3, 0.35, 0.4]),
    phys([2.3, 4.1, 6.3, 8.5, 10.1], [0.25, 0.35, 0.2, 0.45, 0.3])
]

g = graph(x_common, y_experiments, approx=True)
g.xlabel('Voltage, V')
g.ylabel('Current, A') 
g.add_title('Current-Voltage Characteristics')
g.add_params_text(series_names=['Experiment 1', 'Experiment 2', 'Experiment 3'])
g.show()
```

### Paired Datasets

```python
# Independent X and Y sets
x_sets = [
    phys([1, 2, 3], 0.1),
    phys([4, 5, 6], 0.1)
]

y_sets = [
    phys([2, 4, 6], 0.2),
    phys([8, 10, 12], 0.2)
]

g = graph(x_sets, y_sets, approx=True)
g.xlabel('Distance, m')
g.ylabel('Force, N')
g.add_title('Dependencies for Different Conditions')
g.show()
```

### Advanced Features

```python
# Scientific style with method chaining
graph(x, y, approx=True)\
    .style_scientific()\
    .add_title('Experimental Dependency', fontsize=16)\
    .auto_legend(loc='upper left')\
    .add_stats(x=0.65, y=0.15)\
    .xlabel('$t$, s', fontsize=14)\
    .ylabel('$v$, m/s', fontsize=14)\
    .quick_save('experiment', format = 'jpg')
```

## Practical Examples

### Example 1: Experimental Data Processing

```python
# Free fall acceleration experiment data
times = phys([0.1, 0.2, 0.3, 0.4, 0.5], 0.01)  # time, s
distances = phys([0.049, 0.196, 0.441, 0.784, 1.225], 
                [0.001, 0.002, 0.003, 0.004, 0.005])  # distance, m

# Acceleration calculation via LSM (s = gt²/2 => s ~ t²)
times_squared = times ** 2
k, b = lab.weighted_least_squares(times_squared, distances)

# Free fall acceleration g = 2k
g_experimental = 2 * k
print(f"Measured free fall acceleration: {g_experimental}")

# Visualization
graph(times_squared, distances, approx=True)\
    .xlabel('$t^2$, s²')\
    .ylabel('$s$, m')\
    .add_title('Free Fall Acceleration Determination')\
    .add_params_text()\
    .show()
```

### Example 2: Statistical Processing

```python
# Resistance measurement series
resistance_measurements = [
    phys(998, 5), phys(1002, 5), phys(995, 5),
    phys(1005, 10), phys(997, 5), phys(1001, 5)
]

# Statistical processing
mean_resistance = lab.weighted_mean(resistance_measurements)

# LaTeX report generation
report_table = lab.latex_table(
    resistance_measurements,
    header=['No.', 'Resistance, Ω'],
    first_column=list(range(1, 7)),
    caption='Resistance Measurement Results'
)
```

### Example 3: Complex Physics Calculations

```python
# Mathematical pendulum period calculation
length = phys(1.0, 0.01)  # length, m
g = phys(9.81, 0.01)     # gravitational acceleration, m/s²

# T = 2π√(L/g)
period = 2 * np.pi * sqrt(length / g)

# Length vs period dependency
lengths = phys(np.linspace(0.5, 2.0, 10), 0.02)
periods = 2 * np.pi * sqrt(lengths / g)

graph(lengths, periods)\
    .xlabel('Pendulum Length, m')\
    .ylabel('Oscillation Period, s')\
    .add_title('Period vs Length Dependency')\
    .show()
```

## API Reference

### Class phys

**Constructor:**
```python
phys(value, abs_err=0.0)  # value: number, list, np.array
```

**Properties:**
- value - main value
- sigma - absolute uncertainty (read/write) 
- eps - relative uncertainty (read/write)

**Mathematical Operations:**
- +, -, *, /, ** - with automatic uncertainty propagation
- Support for operations with numbers and other phys objects

**Array Methods:**
- sort(), sorted - sorting
- in_order(order) - reordering  
- concatenate() - combining
- append() - adding elements

### Class LabProcessor

**Statistical Methods:**
- weighted_mean(arr) - weighted average
- weighted_least_squares(x, y) - least squares method

**LaTeX Generators:**
- latex_table() - tables
- latex_value() - value formatting  
- e_to_tex() - scientific notation conversion

### Class graph

**Main Methods:**
- __init__(x, y, approx=True) - graph creation
- add_title(), xlabel(), ylabel() - styling
- add_params_text() - approximation parameters
- quick_save() - saving

**Styles:**
- style_scientific() - scientific style
- Full matplotlib compatibility

## Conclusion

PhysLab provides complete toolkit for:
- Working with physical quantities and uncertainties
- Statistical processing of experimental data  
- Professional results visualization
- Automatic scientific report generation

Perfect for educational projects, laboratory works, and scientific research.