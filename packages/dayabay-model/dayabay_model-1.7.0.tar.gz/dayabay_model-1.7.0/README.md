# The model of the Daya Bay Reactor Neutrino experiment

[![python](https://img.shields.io/badge/python-3.11-purple.svg)](https://www.python.org/)
[![pipeline](https://git.jinr.ru/dagflow-team/dayabay-model/badges/main/pipeline.svg)](https://git.jinr.ru/dagflow-team/dayabay-model/commits/main)
[![coverage report](https://git.jinr.ru/dagflow-team/dayabay-model/badges/main/coverage.svg)](https://git.jinr.ru/dagflow-team/dayabay-model/-/commits/main)
[![github](https://img.shields.io/badge/github-public-blue?logo=github)](https://github.com/dagflow-team/dayabay-model)
[![gitlab](https://img.shields.io/badge/gitlab-dev-blue?logo=gitlab)](https://git.jinr.ru/dagflow-team/dayabay-model)
[![github-framework](https://img.shields.io/badge/github-framework-blue?logo=github)](https://github.com/dagflow-team/dag-modelling)
[![pypi-release](https://img.shields.io/badge/pypi-release-blue?logo=pypi&logoColor=green)](https://pypi.org/project/dayabay-model)
[![github-data](https://img.shields.io/badge/github-data-green?logo=github)](https://github.com/dayabay-experiment/dayabay-data-official)
[![pypi-data](https://img.shields.io/badge/pypi-data-green?logo=pypi&logoColor=green)](https://pypi.org/project/dayabay-data-official)
[![zenodo](https://img.shields.io/badge/zenodo-data-green?logo=zenodo&logoColor=green)](https://doi.org/10.5281/zenodo.17587229)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Summary

The repository contains the model of the Daya Bay Reactor Neutrino experiment dedicated to work with Full Daya Bay dataset and perform neutrino oscillation analysis based on gadolinium capture data.

The Daya Bay Reactor Neutrino Experiment took data from 2011 to 2020 in China. It obtained a sample of 5.55 million IBD events with the final-state neutron captured on gadolinium (nGd). This sample was collected by eight identically designed antineutrino detectors (AD) observing antineutrino flux from six nuclear power plants located at baselines between 400 m and 2 km. It covers 3158 days of operation.

The model is able to read any format of the Daya Bay dataset and produce a measurement of sin²2θ₁₃ and Δm²₃₂, consistent with the publication.

## Repositories

- Code:
    * Main: development, CI: https://git.jinr.ru/dagflow-team/dayabay-model
    * Mirror: public access, issue tracker: https://github.com/dagflow-team/dayabay-model
    * PYPI: https://pypi.org/project/dayabay-model
- Data:
    * Full Data Release of the Daya Bay Reactor Neutrino Experiment: https://doi.org/10.5281/zenodo.17587229
    * Analysis dataset, PYPI: https://pypi.org/project/dayabay-model
    * Analysis dataset, GitHub: https://github.com/dayabay-experiment/dayabay-data-official

## Contents 

- [Summary](<#summary>)
- [Repositories](<#repositories>)
- [Overview](<#overview>)
    * [Data model](<#data-model>)
    * [Processing model](<#processing-model>)
    * [Analysis examples](<#analysis-examples>)
- [Working with the model](<#working-with-the-model>)
    * [Installation](<#installation>)
        + [Getting the code](<#getting-the-code>)
            - [From Python Package Index](<#from-python-package-index>)
            - [From GitHub](<#from-github>)
    * [Minimal working examples](<#minimal-working-examples>)
        + [Simple run](<#simple-run>)
        + [Specifying the path to the data](<#specifying-the-path-to-the-data>)
        + [Switching between real data and Asimov pseudo-data](<#switching-between-real-data-and-asimov-pseudo-data>)
    * [Usage scripts](<#usage-scripts>)
    * [Other files](<#other-files>)
        + [src/dayabay_model/](<#src/dayabay_model/>)
        + [src/dayabay_model/bundles/](<#src/dayabay_model/bundles/>)
        + [Unit tests](<#unit-tests>)

## Overview

### Data model

The released Daya Bay data is available in a variety of file formats (ROOT, hdf5, npz, tsv). All files follow the same conceptual schema and provide a set of key/value pairs. File names indicate the set of keys to expect and in some cases the context of the data (e.g. a particular sub-detector).  Values are arrays. For detailed description of the expected file and key names see: [https://github.com/dayabay-experiment/dayabay-data-official](https://github.com/dayabay-experiment/dayabay-data-official).

### Processing model

The user may process the data with their own software while Daya Bay also provides a reference processing framework and a set of processing components based on the dag-modelling package. This framework processes the data through a lazy evaluated directed acyclic data-flow programming graph with a set of functional nodes. 

### Analysis examples

The typical workflow considers installation of the Daya Bay model via PYPI and using it in the analysis from within python. While minimal working examples may be found in this repository more comprehensive cases of the fits and statistical analysis are provided in a dedicated [dayabay-analysis](https://github.com/dagflow-team/dayabay-analysis) repository.

## Working with the model

### Installation

#### Getting the code

##### From Python Package Index

The package may be installed with `pip` as follows:

```bash
pip install dayabay-model
```

The installation installs the `daybay-data-official` python module as a dependency, which provides the analysis version of the Full Daya Bay dataset.

##### From GitHub

To install the model from the GitHub, first, clone the repository.

```bash
git clone https://github.com/dagflow-team/dayabay-model
cd daybay-model
pip install -e .
```

Second, install the contents of the local module as python package, triggering also dependencies installation, including data. Note, that the argument `-e` uses symbolic links to the python files instead of copying, which makes all the modifications of the model immediately accessible.

### Minimal working examples

The minimal working examples are located in the folder `extras/mwe` folder. They are available when the code comes from the GitHub.

#### Simple run

Now one can run the script [run.py](extras/mwe/run.py):

```bash
./extras/mwe/run.py
```

or as

```bash
PYTHONPATH=PWD python extras/mwe/run.py
```

The code:

```python
from dayabay_model import model_dayabay

model = model_dayabay()
print(model.storage["outputs.statistic.full.covmat.chi2cnp"].data)
```

loads the model, calculates, and prints the initial value of the χ² function to the terminal:

```bash
INFO: Model version: model_dayabay
INFO: Source type: npz
INFO: Data path: data
INFO: Concatenation mode: detector_period
INFO: Spectrum correction mode: exponential
INFO: Spectrum correction location: before integration
[705.12741983]
```

The value is essentially non-zero as the initial model does not fit the real data well. 


#### Specifying the path to the data

The path to the data may be specified via `path_data` constructor argument of the `model_dayabay` class as follows:

```python
from dayabay_model import model_dayabay

model = model_dayabay(path_data="dayabay-data-official/npz")
print(model.storage["outputs.statistic.full.pull.chi2cnp"].data)
```

The code may be found in [run-custom-data-path.py](extras/mwe/run-custom-data-path.py) example.


#### Switching between real data and Asimov pseudo-data

The `real` data is loaded to model by default. However, it is possible to switch between `real` and `asimov` datasets with `switch_data(type: str)` method. Here:
- `real` refers to the histograms with IBD candidates of the Full Daya Bay data release.
- `asimov` will use the prediction of the model as an average pseudo-data. The prediction will be fixed.

The example script is [extras/mwe/run-switch-asimov-real-data.py](extras/mwe/run-switch-asimov-real-data.py):

```python
from dayabay_model import model_dayabay

model = model_dayabay()

print("CNP chi-squared (default data):", model.storage["outputs.statistic.full.pull.chi2cnp"].data)

model.switch_data("real")
print("CNP chi-squared (real data):", model.storage["outputs.statistic.full.pull.chi2cnp"].data)

model.switch_data("asimov")
print("CNP chi-squared (asimov data):", model.storage["outputs.statistic.full.pull.chi2cnp"].data)
```

#### Switching between different source types of dayabay-data-official

The `hdf5` dat is loaded to model by default from [dayabay-data-official](https://pypi.org/project/dayabay-data-official/) package. However, it is possible change source type of dataset between `hdf5`, `npz`, `root`, and `tsv`. It can be done via `get_path_data()` function from [dayabay-data-official](https://pypi.org/project/dayabay-data-official/) package.

The example script is [extras/mwe/run-switch-source-type.py](extras/mwe/run-switch-source-type.py):

```python
from dayabay_model import model_dayabay
from dayabay_data_official import get_path_data


model = model_dayabay()
print("χ² CNP (default data):", model.storage["outputs.statistic.full.pull.chi2cnp"].data)

for source_type in ["hdf5", "root", "npz", "tsv"]:
    model = model_dayabay(path_data=get_path_data(source_type))
    print(
        f"χ² CNP ({source_type} data):", model.storage["outputs.statistic.full.pull.chi2cnp"].data
    )
```

### Usage scripts

These are the scripts showing the very basic interfaces of the model. Note, that the analysis scripts are provided in another repository. The main reason for this is that the approach enables us to fix the model version for a long term, but still be able to update and expand the analysis examples in another repository.

The examples on how to use the scripts are given in the corresponding files' headers and also may be found in `tests/shell/*.sh` scripts.

- [dayabay-access.py](extras/scripts/dayabay-access.py) — Demonstrate how to access some of the Daya Bay data from the model.
- [dayabay-plot-all-outputs.py](extras/scripts/dayabay-plot-all-outputs.py) — iterate over each node (group of nodes) of the model and plot it contents with `matplotlib` to a pdf file. The titles and labels are generated based on the yaml file, shared with the model. The script produces the directory structure of pdf files, resembling the internal organization of the storage.
- [dayabay-plot-all-subgraphs.py](extras/scripts/dayabay-plot-all-subgraphs.py) — iterate over each node and plot sub-graph by advancing up to two layers behind the current node and one layer forward. The sub-graphs are saved into graphviz's dot files and may be opened interactively.
- [dayabay-plot-detector-data.py](extras/scripts/dayabay-plot-detector-data.py) — plot time dependent detector data.
- [dayabay-plot-neutrino-rate-data.py](extras/scripts/dayabay-plot-neutrino-rate-data.py) — plot time dependent neutrino rate data.
- [dayabay-print-internal-data.py](extras/scripts/dayabay-print-internal-data.py) — print the contents of the internal storage to the stdout. May print free, constrained or fixed parameters; the internal and final arrays. Print path, values and uncertainties (for parameters), dimensions (for arrays) and their text description, derived from the yaml file.
- [dayabay-print-parameters-latex.py](extras/scripts/dayabay-print-parameters-latex.py) — for each group of parameters creates a latex file with information, including name, description, values and uncertainties.
- [dayabay-print-parameters-text.py](extras/scripts/dayabay-print-parameters-text.py) — save the list of parameters into a text file including names, values and uncertainties.
- [dayabay-print-summary.py](extras/scripts/dayabay-print-summary.py) — print Daya Bay summary data to stdout or to output files. Yields 4 tables: for each of 3 data taking periods and a total one. The results correspond to the Table I from Physical Review Letters 130, 161802 (2023).
- [dayabay-save-detector-response-matrices.py](extras/scripts/dayabay-save-detector-response-matrices.py) — compute and save the detector response matrices and, optionally, plot them.
- [dayabay-save-outputs-to-root.py](extras/scripts/dayabay-save-outputs-to-root.py) — save the memory buffer of each output in the storage to the root file, preserving the location structure.
- [dayabay-save-parameters-to-latex-datax.py](extras/scripts/dayabay-save-parameters-to-latex-datax.py) — save the current values, central values and uncertainties of the parameters to the tex file to be used with [LaTeX datax](https://ctan.org/pkg/datax) package.

### Other files

#### src/dayabay_model/

This is the source folder of the package. In the root it contains:

- [model_dayabay.py](src/dayabay_model/model_dayabay.py) — the model itself. It contains all necessary definitions for reading the input data and building the model, including a few χ² constructions. This is the main part of the data preservation code and contains lots of comments explaining the physics and calculation procedure. This is the first file to be reviewed.
- [model_dayabay.yaml](src/dayabay_model/model_dayabay.yaml) — dictionary with labels. A supplementary file for the model, which includes text and latex labels for the nodes and outputs of the model to be used for printing, plotting and I/O.

#### src/dayabay_model/bundles/

These are the supplementary functions to work with some of the input data, which are called from within a model:

- [refine_neutrino_rate_data.py](src/dayabay_model/bundles/refine_neutrino_rate_data.py) — take averaged with a window of a few weeks neutrino rate data and build arrays with daily data for neutrino rate. The 0-th day is tied to the first Daya Bay's day of data taking. No interpolation is done, the values within the period are assigned to each day of the period.
- [refine_detector_data.py](src/dayabay_model/bundles/refine_detector_data.py) — perform a similar process to the detector data and build arrays with efficiency, livetime and rate of accidentals.
- [sync_neutrino_rate_detector_data.py](src/dayabay_model/bundles/sync_neutrino_rate_detector_data.py) — checks the consistency of the arrays produced by the previous scripts and ensured they are synced in time.
- [refine_lsnl_data.py](src/dayabay_model/bundles/refine_lsnl_data.py) — interpolates and extrapolates input LSNL data.

#### Unit tests

- [tests/test_model_dayabay.py](tests/test_model_dayabay.py) — a unit test, which is run at GitLab CI (continuous integration) on each commit to `main` or to the branch, associated with merge request (pull request). It ensures the model may be run and evaluated.
- [tests/test_data_formats.py](tests/test_data_formats.py) — ensures that the model reading 4 different input format yields consistent results: fully consistent for binary formats, and almost consistent within relative accuracy of 10⁻¹¹ for the text format.
