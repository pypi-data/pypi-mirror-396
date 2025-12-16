# Mobiu-Q

**Mobiu-Q** is a next-generation optimizer built on *Soft Algebra* and *Demeasurement* theory, enabling stable and efficient optimization in quantum variational algorithms (VQE, QAOA).

## ✨ Features

- **+43% improvement** over Adam optimizer in VQE benchmarks
- **Soft Algebra** update rule for stable convergence
- **SPSA Demeasurement** for noisy hardware (95% fewer measurements)
- **Adaptive Trust Ratio** - automatically adjusts to noise levels

## 📦 Installation

```bash
pip install mobiu-q
```

## 🔑 Activation

Get your free license key at [mobiu-q.com](https://mobiu-q.com)

```bash
mobiu-q activate YOUR_LICENSE_KEY
```

Or set environment variable:
```bash
export MOBIU_Q_LICENSE_KEY=your-key
```

## 🚀 Quick Start

### Clean Simulations

```python
import numpy as np
from mobiu_q import MobiuQCore, Demeasurement, get_energy_function

# Load a built-in problem
energy_fn = get_energy_function("h2_molecule")

# Initialize optimizer
opt = MobiuQCore(mode="standard")

# Random starting point
params = np.random.uniform(-np.pi, np.pi, 12)

# Optimization loop
for step in range(100):
    E = energy_fn(params)
    grad = Demeasurement.finite_difference(energy_fn, params)
    params = opt.step(params, grad, E)
    
    if step % 20 == 0:
        print(f"Step {step}: E = {E:.6f}")

# Always end the session!
opt.end()
```

### Noisy Quantum Hardware

```python
# For NISQ devices, use noisy mode + SPSA
opt = MobiuQCore(mode="noisy")

for step in range(100):
    # SPSA: Only 2 measurements per step!
    grad, E = Demeasurement.spsa(energy_fn, params)
    params = opt.step(params, grad, E)

opt.end()
```

## 📊 Built-in Problems

```python
from mobiu_q import list_problems, get_energy_function, get_ground_state_energy

print(list_problems())
# ['h2_molecule', 'lih_molecule', 'transverse_ising', ...]

energy_fn = get_energy_function("lih_molecule")
E0 = get_ground_state_energy("lih_molecule")
print(f"Ground state energy: {E0}")
```

## ⚙️ API Reference

### MobiuQCore

```python
MobiuQCore(
    license_key=None,     # Your license key (or use env var)
    mode="standard",      # 'standard' or 'noisy'
    base_lr=None,         # Learning rate (auto-set by mode)
    offline_fallback=True # Fall back to Adam if API unavailable
)
```

**Methods:**
- `step(params, gradient, energy)` → Updated parameters
- `end()` → End session (important!)
- `reset()` → Reset for new optimization

### Demeasurement

- `Demeasurement.finite_difference(fn, params)` - Accurate, 2N measurements
- `Demeasurement.parameter_shift(fn, params)` - Exact for quantum circuits
- `Demeasurement.spsa(fn, params)` - Noisy-resistant, only 2 measurements!

## 💰 Pricing

| Tier | Runs/Month | Price |
|------|------------|-------|
| Free | 20 | $0 |
| Pro | Unlimited | $29/month |

A "run" is one complete optimization session (start → steps → end).

Sessions ended within 60 seconds with <5 steps don't count.

## 🔒 Security

Your optimization runs on Mobiu's secure cloud infrastructure. The core Soft Algebra logic never leaves our servers - your client only sends parameters and gradients.

## 📄 License

Proprietary - see LICENSE.md

© Mobiu Technologies, 2025
