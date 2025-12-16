# ThalosForge

**Enterprise optimization API — the CPLEX/Gurobi alternative.**

```bash
pip install thalosforge[cloud]
```

## Quick Start

```python
import thalosforge as tf

# Configure with your API key (get one at thalosforge.com/pricing)
tf.configure(api_key="tf_...")

# Optimize
result = tf.optimize(
    func="sum(x**2)",
    bounds=[(-5, 5)] * 100
)

print(result.status)     # Status.OPTIMAL
print(result.objective)  # 1.234e-08
print(result.x)          # [0.0001, -0.0002, ...]
```

## Why ThalosForge?

| Feature | ThalosForge | CPLEX | Gurobi |
|---------|-------------|-------|--------|
| Installation | `pip install` | License manager + installer | License manager + installer |
| Setup time | 30 seconds | 30+ minutes | 30+ minutes |
| Cloud-ready | ✅ Built-in | Extra setup | Extra setup |
| High-dimensional (1000D+) | ✅ Optimized | Slow | Slow |
| Derivative-free | ✅ | ❌ | ❌ |
| Pricing | Pay-as-you-go | $15K+/year | $12K+/year |

## API Key

Get your API key at [thalosforge.com/pricing](https://www.thalosforge.com/pricing.html)

Set it in code:
```python
tf.configure(api_key="tf_...")
```

Or via environment variable:
```bash
export THALOSFORGE_API_KEY=tf_...
```

## Objective Functions

Pass objective as a math expression string:

```python
# Sphere
result = tf.optimize("sum(x**2)", bounds)

# Rastrigin
result = tf.optimize("10*n + sum(x**2 - 10*cos(2*pi*x))", bounds)

# Rosenbrock
result = tf.optimize("sum(100*(x[1:]-x[:-1]**2)**2 + (1-x[:-1])**2)", bounds)
```

Available functions: `sum`, `prod`, `mean`, `abs`, `sqrt`, `exp`, `log`, `sin`, `cos`, `tan`, `pi`, `e`

Variables: `x` (solution vector), `n` (dimensions)

## Engines

### QuantumJolt (High-Dimensional)
Best for 100-10,000+ dimensions. SPSA-based, derivative-free.

```python
result = tf.optimize(func, bounds, engine="quantumjolt", max_evaluations=5000)
```

### DSS (Deterministic)
100% reproducible. Same inputs = identical outputs. Regulatory-friendly.

```python
result = tf.optimize(func, bounds, engine="dss")
```

### Kestrel (Constrained)
Linear constraints, inequality bounds.

```python
result = tf.optimize(
    func="x[0] + x[1]",
    bounds=[(0, 10), (0, 10)],
    engine="kestrel",
    constraints=[
        {"expression": "x[0] + x[1]", "type": "leq", "rhs": 15},
    ]
)
```

## Result Object

```python
result.status       # Status.OPTIMAL, FEASIBLE, INFEASIBLE, TIMEOUT
result.objective    # Final objective value
result.x            # Solution vector (list)
result.iterations   # Number of iterations
result.evaluations  # Function evaluations
result.time         # Solve time in seconds
result.engine       # Engine used

# Export
result.to_json("solution.json")
```

## Usage Tracking

```python
# Check your usage
usage = tf.usage()
print(f"Used: {usage['optimizations_used']}/{usage['optimizations_limit']}")
```

## Pricing

| Tier | Price | Optimizations/mo | Max Dims |
|------|-------|------------------|----------|
| Free | $0 | 100 | 20 |
| Developer | $499/mo | 10,000 | 500 |
| Professional | $2,499/mo | 100,000 | 2,000 |
| Enterprise | Custom | Unlimited | Unlimited |

## Support

- Documentation: https://www.thalosforge.com/documentation.html
- Email: support@thalosforge.com
- Enterprise: enterprise@thalosforge.com

## License

© 2025 ThalosForge Inc. All rights reserved.
