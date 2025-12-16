# Mobiu-Q

**Soft Algebra Optimizer for Quantum Computing**

Mobiu-Q achieves **+62% on VQE** and **+20% on QAOA** compared to Adam optimizer, using a novel Soft Algebra approach that's resilient to quantum noise.

## Installation

```bash
pip install mobiu-q
```

## Quick Start

### VQE (Molecular Simulation)

```python
from mobiu_q import MobiuQCore, Demeasurement

# Initialize optimizer for VQE
opt = MobiuQCore(
    license_key="your-license-key",
    mode="standard",      # or "noisy" for hardware
    problem="vqe"         # default
)

# Optimization loop
for step in range(100):
    energy = compute_energy(params)
    gradient = Demeasurement.finite_difference(energy_fn, params)
    params = opt.step(params, gradient, energy)

opt.end()
```

### QAOA (Combinatorial Optimization)

```python
from mobiu_q import MobiuQCore, Demeasurement

# Initialize optimizer for QAOA
opt = MobiuQCore(
    license_key="your-license-key",
    mode="noisy",         # QAOA typically uses SPSA
    problem="qaoa"        # Use Super-Equation Δ†
)

# Optimization loop
for step in range(150):
    energy = qaoa_expectation(params)
    gradient = spsa_gradient(energy_fn, params)
    params = opt.step(params, gradient, energy)

opt.end()
```

## Benchmarks

### VQE (Quantum Chemistry)

| Molecule | Improvement vs Adam | p-value |
|----------|---------------------|---------|
| H₂       | +62%                | < 10⁻⁵⁷ |
| LiH      | +50.6%              | < 10⁻¹² |
| HeH⁺     | +68%                | < 10⁻⁴⁰ |

### QAOA (Combinatorial, noise=10%)

| Problem           | Depth | Improvement | p-value |
|-------------------|-------|-------------|---------|
| MaxCut            | p=5   | +38.49%     | < 0.001 |
| Vertex Cover      | p=5   | +35.77%     | 0.011   |
| Max Independent Set | p=5 | +30.62%     | < 0.001 |

### Hardware Validation

Tested on **IBM Quantum Eagle (127-qubit)**:
- **Adam**: Crashed to -1.681 Ha (non-physical)
- **Mobiu-Q**: Converged to -1.176 Ha (99.6% accuracy)

## Parameters

| Parameter | Values | Description |
|-----------|--------|-------------|
| `mode` | `"standard"`, `"noisy"` | Gradient type |
| `problem` | `"vqe"`, `"qaoa"` | Problem type |
| `base_lr` | float | Base learning rate (auto-set by mode) |

## How It Works

### VQE: Trust Ratio

For smooth energy landscapes (molecular chemistry), Mobiu-Q uses the **Trust Ratio**:

```
φ = |S.real| / (|S.real| + |S.soft| + ε)
```

High trust = stable gradient = larger learning rate.

### QAOA: Super-Equation Δ†

For rugged combinatorial landscapes, Mobiu-Q uses the **Super-Equation** from Universal Attention Field Theory:

```
Δ† = κ · Du[sin(πS)] · g(τ,α) · Γ(a,β) · √(b·g(τ,α))
```

This identifies optimal "emergence points" where the optimization should act aggressively.

## Pricing

- **Free**: 20 runs/month
- **Pro**: $19/month unlimited

Get your license at [app.mobiu.ai](https://app.mobiu.ai)

## License

Proprietary. See [LICENSE](LICENSE) for details.

## Citation

```bibtex
@software{mobiu_q,
  author = {Angel, Ido},
  title = {Mobiu-Q: Soft Algebra Optimizer for Quantum Computing},
  year = {2025},
  url = {https://github.com/mobiuai/mobiu-q}
}
```

## References

- Klein, M. & Maimon, O. "Foundations of Soft Logic" (2023)
- Angel, I. "Universal Attention Field Theory" (2025)

---

Made with ❤️ by [Mobiu Technologies](https://mobiu.ai)