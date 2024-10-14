![STScI Logo](_static/stsci_header.png)

# JWST Pipeline Notebooks $${\color{red}UNDER---CONSTRUCTION}$$

> [!IMPORTANT]
> JWST requires a C compiler for dependencies and is currently limited to Python 3.10, 3.11, or 3.12.

> [!NOTE]
> Linux and MacOS platforms are tested and supported.  Windows is not currently supported.

The ``jwst_pipeline_notebooks`` repository contains python-based Jupyter notebooks that illustrate how to process JWST data through the STScI science calibration pipeline (``jwst``;  [https://github.com/spacetelescope/jwst](https://github.com/spacetelescope/jwst)).  An overview of the pipeline can be found at [https://jwst-docs.stsci.edu/jwst-science-calibration-pipeline](https://jwst-docs.stsci.edu/jwst-science-calibration-pipeline).

Notebooks are organized according to instrument and observing mode.  Each notebook is designed to process data from uncalibrated raw FITS files to end-stage Level 3 data products (calibrated imaging mosaics, 3-D data cubes, 1-D extracted spectra, etc.).  These notebooks by default run in 'demo' mode, for which they will download and process example data drawn from the [MAST archive](https://archive.stsci.edu/).  They are, however, designed to be simple to run on arbitrary local data sets as well by configuring input directories accordingly.

These notebooks are modular, allowing users to enable or disable different stages of processing.  Likewise, they provide examples of how to customize pipeline processing for specific science cases.

The following table summarizes the notebooks currently available and the JWST [pipeline versions](https://jwst-docs.stsci.edu/jwst-science-calibration-pipeline/jwst-operations-pipeline-build-information) that they have been tested with:

| Instrument | Observing Mode | JWST Build | ``jwst`` version | Notes                                         |
|------------|----------------|------------|--------------------------|-----------------------------------------------|
| MIRI       | MRS            | 11.0, 11.1       | 1.15.1, 1.16.0                   |                                               |
| NIRISS     | Imaging        | 11.0       | 1.15.1                   |                                               |

## Reference Files

As of October 2024, the JWST pipeline will automatically select the best reference file context appropriate to each pipeline version by default.  The notebooks provided here allow users to override this default if desired and choose specific contexts instead.  See [https://jwst-docs.stsci.edu/jwst-science-calibration-pipeline#JWSTScienceCalibrationPipeline-crds_contextChoosingacontext](Choosing a Context) for guidance.

## Installation

### Individual Notebooks

For advanced users, these notebooks can be downloaded individually from the GitHub repository and run in any python environment in which the [``jwst``](https://github.com/spacetelescope/jwst) package meeting the indicated minimum version has been installed.  Note that some notebooks have additional dependencies (e.g., [jdaviz](https://github.com/spacetelescope/jdaviz/)) as given in the associated requirements files.

### Package Installation

If desired, you can also clone the entire ``jwst_pipeline_notebooks`` repository to your local computer and set up a new virtual or conda environment
to avoid version conflicts with other packages you may have installed, for example:

    conda create -n jpnb python=3.11
    conda activate jpnb
    git clone https://github.com/spacetelescope/jwst_pipeline_notebooks.git

Next, move into the directory of the notebook you want to install and set up the requirements:

    cd jwst_pipeline_notebooks/notebooks/<whatever-notebook>
    pip install -r requirements.txt
    jupyter notebook

We recommend setting up a new environment for each notebook to ensure that there are no conflicting dependencies.

## Help

If you uncover any issues or bugs, you can open an issue on GitHub. For faster responses, however, we encourage you to submit a [JWST Help Desk Ticket](jwsthelp.stsci.edu)
