# JWST Pipeline Notebooks

![STScI Logo](_static/stsci_header.png)

> [!IMPORTANT]
> JWST requires a C compiler for dependencies and is currently limited to Python 3.10, 3.11, or 3.12.

> [!NOTE]
> Linux and MacOS platforms are tested and supported.  Windows is not currently supported.

The ``jwst_pipeline_notebooks`` repository contains python-based Jupyter notebooks that illustrate how to process JWST data through the STScI science calibration pipeline (``jwst``;  [https://github.com/spacetelescope/jwst](https://github.com/spacetelescope/jwst)).  An overview of the pipeline can be found at [https://jwst-docs.stsci.edu/jwst-science-calibration-pipeline](https://jwst-docs.stsci.edu/jwst-science-calibration-pipeline), along with information about any changes in the [latest pipeline version](https://jwst-docs.stsci.edu/jwst-science-calibration-pipeline/jwst-operations-pipeline-build-information).

Notebooks are organized according to instrument and observing mode.  Each notebook is designed to process data from uncalibrated raw FITS files to end-stage Level 3 data products (calibrated imaging mosaics, 3-D data cubes, 1-D extracted spectra, etc.).  These notebooks by default run in 'demo' mode, for which they will download and process example data drawn from the [MAST archive](https://archive.stsci.edu/).  They are, however, designed to be simple to run on arbitrary local data sets as well by configuring input directories accordingly.

These notebooks are modular, allowing users to enable or disable different stages of processing.  Likewise, they provide examples of how to customize pipeline processing for specific science cases. 

The following table summarizes the notebooks currently available:

| Instrument | Observing Mode | JWST Build | Minimum ``jwst`` version | Notes                                         |
|------------|----------------|------------|--------------------------|-----------------------------------------------|
| MIRI       | MRS            | 11.0       | 1.15.1                   |                                               |
| NIRISS     | Imaging        | 11.0       | 1.15.1                   |                                               |

While each notebook has been constructed for use with a given minimum version of the ``jwst`` pipeline software, they are generally compatible with more-recent versions.

## Installation

### Individual Notebooks

These notebooks can be downloaded individually from the GitHub repository and run in any python environment in which the [``jwst``](https://github.com/spacetelescope/jwst) package meeting the indicated minimum version has been installed.  Note that some notebooks have additional dependencies (e.g., [jdaviz](https://github.com/spacetelescope/jdaviz/)) as given in the associated requirements files.

### Package Installation

If desired, you can also clone the entire ``jwst_pipeline_notebooks`` repository to your local computer and set up a new virtual or conda environment
to avoid version conflicts with other packages you may have installed, for example::

    conda create -n jpnb python=3.9
    conda activate jpnb
    git clone https://github.com/spacetelescope/jwst_pipeline_notebooks.git

Next, move into the directory of the notebook you want to install and set up the requirements::

    cd jwst_pipeline_notebooks/notebooks/<whatever-notebook>
    pip install -r requirements.txt
    jupyter notebook

## Help

If you uncover any issues or bugs, you can open an issue on GitHub. For faster responses, however, we encourage you to submit a [JWST Help Desk Ticket](jwsthelp.stsci.edu)
