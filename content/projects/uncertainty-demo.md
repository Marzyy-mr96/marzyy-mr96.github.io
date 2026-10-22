---
title: "Interactive: Monte Carlo vs. Dimension Reduction"
category: Computational Methods
summary: A hands-on demo of uncertainty propagation. Watch Monte Carlo build a response distribution sample by sample, and compare it with a dimension-reduction estimate that needs only 17 model runs.
status: Interactive demo
order: 3
featured: yes
tools: JavaScript, SVG
---
## The example

A steel cantilever beam, 3 m long, carries a point load *P* at its tip and a uniform load *w* along its length. Its tip deflection is

*δ = P·L³ / (3·E·I) + w·L⁴ / (8·E·I)*

Four inputs are uncertain and treated as independent normal variables: the loads *P* (mean 20 kN) and *w* (mean 5 kN/m), the elastic modulus *E* (mean 200 GPa), and the moment of inertia *I* (mean 8 × 10⁻⁵ m⁴). Use the sliders to set how uncertain each one is.

{{demo}}

## How the three methods differ

- **Monte Carlo simulation** samples all inputs at random and evaluates the model for each sample. It is general and becomes accurate with enough samples, but every sample is one full model run.
- **FOSM** linearizes the model around the mean inputs. It needs only a handful of runs (9 here) but gives only a mean and standard deviation, and it loses accuracy when the model is strongly nonlinear.
- **Multiplicative dimension reduction (M-DRM)** approximates the model as a product of one-variable functions. It evaluates the model at a few Gauss–Hermite points along each input, holding the others at their means (4 × 4 + 1 = 17 runs here), and combines these to estimate the response moments.

The orange curve is a lognormal distribution matched to the M-DRM mean and standard deviation, for illustration. With large input uncertainties, compare how FOSM and M-DRM track the Monte Carlo reference.

*This is a simple teaching example written for this website. It is not the model, data, or results of the thesis or the manuscript under review.*
