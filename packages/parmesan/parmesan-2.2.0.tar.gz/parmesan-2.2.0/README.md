# 🧀 PARMESAN

**P**ython **A**tmospheric **R**esearch program for **ME**teorological **S**cientific **AN**alysis

[![pipeline status](https://gitlab.com/tue-umphy/software/parmesan/badges/master/pipeline.svg)](https://gitlab.com/tue-umphy/software/parmesan/-/pipelines)
[![coverage report](https://gitlab.com/tue-umphy/software/parmesan/badges/master/coverage.svg)](https://tue-umphy.gitlab.io/software/parmesan/coverage-report/)
[![documentation](https://img.shields.io/badge/documentation-here%20on%20GitLab-brightgreen.svg)](https://tue-umphy.gitlab.io/software/parmesan)
[![Downloads](https://static.pepy.tech/badge/parmesan)](https://pepy.tech/project/parmesan)
[![JOSS paper](https://joss.theoj.org/papers/10.21105/joss.06127/status.svg)](https://doi.org/10.21105/joss.06127)

## What can `PARMESAN` do?

PARMESAN is targeted at meteorologists/scientists doing atmospheric measurements who want to analyse their obtained time series, calculate typical temperature, wind, humidity, atmospheric stability and turbulence parameters.
PARMESAN provides basic building blocks for typical meteorological calculations and can be easily expanded as equations are based on symbolic mathematics that can be recombined and repurposed.

#### 🔢 Physical Calculations

- 📉 calculating [**power spectra** of timeseries](https://tue-umphy.gitlab.io/software/parmesan/notebooks/spectrum.html)
- 📉 calculating [**structure functions** of timeseries](https://tue-umphy.gitlab.io/software/parmesan/notebooks/structure.html)
- ⏱ calculating [**temporal cycles**](https://tue-umphy.gitlab.io/software/parmesan/api/parmesan.aggregate.html#parmesan.aggregate.temporal_cycle) (e.g. diurnal/daily cycles)
- 🌫 calculating several [**humidity** measures](https://tue-umphy.gitlab.io/software/parmesan/api/parmesan.gas.humidity.html)
- 🌡 calculating several [**temperature** measures](https://tue-umphy.gitlab.io/software/parmesan/api/parmesan.gas.temperature.html)
- 📜 handling [**physical units** and checking **bounds**](https://tue-umphy.gitlab.io/software/parmesan/settings.html)
- 🍃 [**wind** calculations](https://tue-umphy.gitlab.io/software/parmesan/api/parmesan.wind.html) calculations
- 💨 [**turbulence parameters**](https://tue-umphy.gitlab.io/software/parmesan/api/parmesan.turbulence.html)
- 🔢 based on reusable [SymPy](https://sympy.org) symbolic mathematics

#### ❓ Why not `metpy`?

While [`metpy`](https://unidata.github.io/MetPy) provides much functionality to handle spatial weather data, it is less focused on timeseries/turbulence analysis such as spectral analysis. See [here](https://tue-umphy.gitlab.io/software/parmesan#why-not-metpy) for a more detailed comparison.


#### 🛠️ Inner Workings

PARMESAN uses...

- [SymPy](https://sympy.org) to do the math. PARMESAN derives meteorological equations with it and auto-generates Python functions and documentation based on SymPy expressions.
- [pint](https://pint.readthedocs.io/) to handle physical units.
- [pint-pandas](https://github.com/hgrecco/pint-pandas) to enable handling units in [pandas](https://pandas.pydata.org/)-DataFrames.
- [numpy](https://numpy.org) and [scipy](https://scipy.org/) for the numerics
- [rich](https://rich.readthedocs.io/) for pretty terminal output like progress bars
- [matplotlib](https://matplotlib.org/) for plotting

## 📦 Installation

Tagged versions of `PARMESAN` are available [on PyPi](https://pypi.org/project/parmesan/).
You can install the latest tagged version of `PARMESAN` via

```bash
# make sure you have pip installed
# Debian/Ubuntu:  sudo apt update && sudo apt install python3-pip
# Manjaro/Arch:  sudo pacman -Syu python-pip

# (optional) Then it's good practice to generate a virtual environment:
python3 -m venv parmesan-venv
source parmesan-venv/bin/activate

# Then install PARMESAN
python3 -m pip install -U parmesan
```

To install the latest development version of `PARMESAN` directly from GitLab, run

```bash
# make sure to have pip installed, see above
python3 -m pip install -U git+https://gitlab.com/tue-umphy/software/parmesan
```

You may also use [our workgroup Arch/Manjaro repository](https://gitlab.com/tue-umphy/workgroup-software/repository) and install the `python-parmesan` package with your favourite software installer, for example with `pacman`:

```bash
sudo pacman -Syu python-parmesan
```

## 📖 Documentation

Documentation can be found [here on GitLab](https://tue-umphy.gitlab.io/software/parmesan).

If you have a question or a problem with PARMESAN, you may [open an issue on GitLab](https://gitlab.com/tue-umphy/software/parmesan/-/issues/new).

## ➕ Contributing to PARMESAN

If you'd like to contribute to PARMESAN, e.g. by adding new features or fixing bugs or just to run the test suite or generate the documentation locally, read the [`CONTRIBUTING.md`-file](https://gitlab.com/tue-umphy/software/parmesan/-/blob/master/CONTRIBUTING.md).
