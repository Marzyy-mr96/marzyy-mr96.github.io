---
title: Uncertainty in Nonlinear Reinforced Concrete Response
category: Structural Reliability
summary: M.Sc. research on how uncertainty in materials and dimensions propagates through nonlinear analysis of reinforced concrete frames, and on reducing the computational cost of doing so.
status: M.Sc. thesis (2022) · Journal manuscript under review
order: 2
featured: yes
tools: Python, NumPy, pandas, TaRa (nonlinear finite-element program)
---
## Why it matters

Engineers rarely know the exact strength of concrete, the yield strength of reinforcing steel, or the as-built dimensions of a member. These uncertainties change not only the expected response of a structure but also its spread and its extremes, which is what matters for safety and risk.

Monte Carlo simulation answers this directly by running the model thousands of times with randomly sampled inputs. For nonlinear finite-element models of reinforced concrete, where each run is expensive, that quickly becomes impractical.

## Research question

How can the effect of structural uncertainties on the response of reinforced concrete frames be evaluated reliably, at a fraction of the computational cost of brute-force simulation?

## Approach

- Wrote Python implementations of three families of reliability methods: **Monte Carlo simulation** (the reference), **First-Order Second-Moment (FOSM)** analysis (fast but locally linear), and **dimension-reduction methods**, which estimate statistical moments of the response from a small, structured set of model runs.
- Coupled these methods with the **TaRa** nonlinear fiber-based finite-element program through its input and output files, automating hundreds of nonlinear analyses.
- Compared the methods on reinforced concrete members and frames, and examined which uncertain inputs contribute most to response variability.

The interactive demo below shows the core idea on a simple textbook example (not the thesis models).

## Thesis and publication

- M.Sc. thesis, Tarbiat Modares University (2022), advised by Prof. Masoud Soltani: *An approximate method to consider structural uncertainties in the response evaluation of reinforced concrete frames.*
- **Allahyari, M.**, & Soltani, M. *An efficient framework for uncertainty propagation in nonlinear reinforced concrete analysis using multiplicative dimension reduction and Laplace-transform maximum entropy.* PLOS ONE, under review.

[Try the interactive demo →](projects/uncertainty-demo.html)
