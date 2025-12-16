# Mobiu-Q

**The VQE Optimizer Built for Quantum Noise.**

Mobiu-Q uses Soft Algebra to achieve **62% better convergence** than Adam on VQE molecular simulations. Validated on IBM Quantum hardware.

## 🎯 What is Mobiu-Q?

Mobiu-Q is a **VQE-optimized optimizer** that prevents variational collapse on noisy quantum hardware. While Adam and other classical optimizers chase noise into non-physical solutions, Mobiu-Q's Trust Ratio mechanism knows when to stop.

### Why VQE?

Mobiu-Q is specifically designed and validated for **Variational Quantum Eigensolver (VQE)** problems:
- Molecular ground state estimation
- Quantum chemistry simulations  
- Material science calculations

For VQE, Mobiu-Q provides significant advantages over Adam. Other quantum algorithms (like QAOA) may not see the same benefits.

---

## 🚀 Quick Start

```bash
pip install mobiu-q
```

```python
from mobiu_q import MobiuQCore, Demeasurement

# Initialize optimizer
opt = MobiuQCore(license_key="your-key", mode="standard")

# VQE optimization loop
for step in range(100):
    energy = energy_fn(params)
    grad = Demeasurement.finite_difference(energy_fn, params)
    params = opt.step(params, grad, energy)

opt.end()
```

---

## 📊 Results

### IBM Hardware Validation (Dec 2025)

| Optimizer | H₂ Final Energy | Ground State (-1.174 Ha) |
|-----------|-----------------|--------------------------|
| Adam | -1.681 Ha | ❌ FAILED (crashed into noise) |
| **Mobiu-Q** | **-1.176 Ha** | ✅ SUCCESS (gap: 0.002 Ha) |

### Simulation Benchmarks

| Problem | Mobiu-Q vs Adam |
|---------|-----------------|
| H₂ VQE | **+62%** better convergence |
| LiH VQE | **+45%** better convergence |
| VQE + Shot Noise | **+9%** better convergence |

---

## ⚙️ Modes

| Mode | Learning Rate | Best For |
|------|---------------|----------|
| `standard` | 0.01 | Clean simulations, statevector |
| `noisy` | 0.02 | Real hardware (IBM, IonQ, Rigetti) |

```python
# For simulators
opt = MobiuQCore(license_key="xxx", mode="standard")

# For real quantum hardware
opt = MobiuQCore(license_key="xxx", mode="noisy")
```

---

## 🔬 Gradient Estimation

```python
from mobiu_q import Demeasurement

# For clean simulations (2*N function calls)
grad = Demeasurement.finite_difference(energy_fn, params)

# For noisy environments (only 2 function calls!)
grad, energy = Demeasurement.spsa(energy_fn, params, c_shift=0.1)
```

---

## 🔄 Multi-Seed Experiments

```python
opt = MobiuQCore(license_key="your-key", mode="standard")

for seed in range(40):
    np.random.seed(seed)
    params = initialize_params()
    
    for step in range(100):
        energy = energy_fn(params)
        grad = Demeasurement.finite_difference(energy_fn, params)
        params = opt.step(params, grad, energy)
    
    results.append(energy_fn(params))
    opt.new_run()  # Reset state for next seed

opt.end()  # Close session
```

---

## 🔥 Full Example: IBM Hardware VQE

```python
from qiskit_ibm_runtime import QiskitRuntimeService, EstimatorV2
from mobiu_q import MobiuQCore, Demeasurement

# Connect to IBM Quantum
service = QiskitRuntimeService(channel="ibm_quantum")
backend = service.least_busy(simulator=False, min_num_qubits=5)
estimator = EstimatorV2(mode=backend)

# Initialize Mobiu-Q for noisy hardware
opt = MobiuQCore(license_key="your-key", mode="noisy")

# VQE optimization
for step in range(60):
    grad, energy = Demeasurement.spsa(
        lambda p: estimator.run([(circuit, observable)]).result()[0].data.evs.item(),
        params,
        c_shift=0.12
    )
    params = opt.step(params, grad, energy)

opt.end()
```

---

## 📚 Built-in VQE Problems

```python
from mobiu_q import list_problems, get_energy_function, get_ground_state_energy

print(list_problems())
# ['h2_molecule', 'lih_molecule', 'transverse_ising', 'heisenberg_xxz', ...]

# Get H2 molecule VQE
energy_fn = get_energy_function("h2_molecule")
E0 = get_ground_state_energy("h2_molecule")
```

---

## 💳 Pricing

| Plan | Price | Runs |
|------|-------|------|
| Free | $0 | 5 VQE runs/month |
| Pro | $19/month | Unlimited |

Get your license at [app.mobiu.ai](https://app.mobiu.ai)

---

## ⚠️ Scope

Mobiu-Q is optimized for **VQE** (Variational Quantum Eigensolver) problems. 

Other quantum algorithms like QAOA may not see significant improvements over Adam. We are actively researching extensions to other domains.

---

## 📖 Learn More

- [Website](https://mobiu.ai)
- [Hardware Validation Report](https://mobiu.ai/wp-content/uploads/2025/12/investment_whitepaper.pdf)
- [PyPI Package](https://pypi.org/project/mobiu-q/)

---

© 2025 Mobiu Technologies