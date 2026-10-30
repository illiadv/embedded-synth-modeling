# Modeling of sound synthesis algorithms in embedded systems
![CI](https://github.com/illiadv/embedded-synth-modeling/actions/workflows/main.yml/badge.svg)

Comparison of different sound synthesis implementations in the context of embedded firmware.

The goals of this project are: 
- to determine the impact of different synthesis parameters on quantitative signal metrics and performance (execution speed, memory usage, SNR etc);
- to compare different sound synthesis algorithms in the context of embedded systems;
- to explore the possibilities of automated simulation modeling using modern tools.

The target device is an ARM Cortex-M4 CPU simulated using Antmicro's [Renode framework](https://github.com/renode/renode).

The sound synthesis algorithms are implemented as a [library](https://github.com/illiadv/embedded-synth-lib) and with different firmware implemenations are built using link-time substitution.
The Github Actions workflow builds and evaluates 36 different implemenations. The results are aggregated into a web-hosted [modeling report](https://illiadv.github.io/embedded-synth-modeling/).
