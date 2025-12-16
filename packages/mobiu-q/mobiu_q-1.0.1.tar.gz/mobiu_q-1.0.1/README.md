# Mobiu-Q

**Mobiu-Q** is a next-generation optimizer built on *Soft Algebra* and *Demeasurement* theory, enabling stable and efficient optimization in quantum variational algorithms (VQE, QAOA).

## ✨ Features

- **+43% improvement** over Adam optimizer in VQE benchmarks
- **99.68% accuracy** on LiH molecule optimization
- **Soft Algebra** update rule for stable convergence
- **SPSA Demeasurement** for noisy hardware (95% fewer measurements)
- **Adaptive Trust Ratio** - automatically adjusts to noise levels

## 📦 Installation

```bash
pip install mobiu-q
```

## 🔑 Get Your License Key

Get your free license key at [app.mobiu.ai](https://app.mobiu.ai)

Then either:

**Option 1:** Set environment variable (recommended):
```bash
export MOBIU_Q_LICENSE_KEY=your-license-key
```

**Option 2:** Pass directly in code:
```python
opt = MobiuQCore(license_key="your-license-key")
```

## 🚀 Quick Start

### Clean Simulations

```python
import numpy as np
from mobiu_q import MobiuQCore, Demeasurement, get_energy_function

# Load a built-in problem
energy_fn = get_energy_function("h2_molecule")

# Initialize optimizer (uses MOBIU_Q_LICENSE_KEY env var)
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
from mobiu_q import MobiuQCore, Demeasurement, get_energy_function

energy_fn = get_energy_function("h2_molecule")

# For NISQ devices, use noisy mode + SPSA
opt = MobiuQCore(mode="noisy")

params = np.random.uniform(-np.pi, np.pi, 12)

for step in range(100):
    # SPSA: Only 2 measurements per step!
    grad, E = Demeasurement.spsa(energy_fn, params)
    params = opt.step(params, grad, E)

opt.end()
```

### Custom Problem (Your Own Hamiltonian)

```python
import numpy as np
from mobiu_q import MobiuQCore, Demeasurement

# Define your own energy function
def my_energy_fn(params):
    # Your quantum circuit / Hamiltonian here
    return np.sum(params**2)  # Example

opt = MobiuQCore(mode="standard")
params = np.random.uniform(-1, 1, 10)

for step in range(100):
    E = my_energy_fn(params)
    grad = Demeasurement.finite_difference(my_energy_fn, params)
    params = opt.step(params, grad, E)

opt.end()
```

## 📊 Built-in Problems

```python
from mobiu_q import list_problems, get_energy_function, get_ground_state_energy

print(list_problems())
# ['h2_molecule', 'lih_molecule', 'transverse_ising', 'heisenberg_xxz', 
#  'xy_model', 'h3_chain', 'ferro_ising', 'antiferro_heisenberg', 
#  'be2_molecule', 'he4_atom']

energy_fn = get_energy_function("lih_molecule")
E0 = get_ground_state_energy("lih_molecule")
print(f"Ground state energy: {E0}")
```

## ⚙️ API Reference

### MobiuQCore

```python
MobiuQCore(
    license_key=None,     # Your license key (or use MOBIU_Q_LICENSE_KEY env var)
    mode="standard",      # 'standard' (clean) or 'noisy' (quantum hardware)
    base_lr=None,         # Learning rate (auto-set by mode)
    offline_fallback=True # Fall back to plain Adam if API unavailable
)
```

**Methods:**
- `step(params, gradient, energy)` → Returns updated parameters
- `end()` → End session (important - always call this!)
- `reset()` → Reset optimizer for new optimization

### Demeasurement

| Method | Measurements | Best For |
|--------|--------------|----------|
| `finite_difference(fn, params)` | 2N | Clean simulations |
| `parameter_shift(fn, params)` | 2N | Exact quantum gradients |
| `spsa(fn, params)` | 2 | Noisy quantum hardware |

## 💰 Pricing

| Tier | Runs/Month | Price |
|------|------------|-------|
| Free | 20 | $0 |
| Pro | Unlimited | $19/month |

**What counts as a "run"?**
- A run = one optimization session (start → steps → end)
- Sessions ended within 60 seconds with <5 steps are free (grace period)

Get Pro at [app.mobiu.ai](https://app.mobiu.ai)

## 🔒 Security & Privacy

- Your optimization runs on Mobiu's secure cloud (Google Cloud)
- The core Soft Algebra logic stays on our servers
- Your client only sends: parameters, gradients, energy values
- We don't store your data beyond the session

## 🐛 Troubleshooting

**"License key required"**
→ Set your license key via environment variable or pass it directly

**"Monthly limit reached"**
→ Upgrade to Pro or wait for next month

**"Cannot connect to API"**
→ Check internet connection. If offline_fallback=True, it will use plain Adam

## 📧 Support

- Email: ai@mobiu.ai

## 📄 License

Proprietary - see LICENSE.md

© Mobiu Technologies, 2025