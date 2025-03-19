![STScI Logo](_static/stsci_header.png)

# JWST Pipeline Notebooks

> [!IMPORTANT]
> JWST requires a C compiler for dependencies and is currently limited to Python 3.10, 3.11, or 3.12.

> [!NOTE]
> Linux and MacOS platforms are tested and supported.  Windows is not currently supported.

The ``jwst-pipeline-notebooks`` repository contains python-based Jupyter notebooks that illustrate how to process JWST data through the STScI science calibration pipeline (``jwst``;  [https://github.com/spacetelescope/jwst](https://github.com/spacetelescope/jwst)).  An overview of the pipeline can be found at [https://jwst-docs.stsci.edu/jwst-science-calibration-pipeline](https://jwst-docs.stsci.edu/jwst-science-calibration-pipeline).

Notebooks are organized according to instrument and observing mode.  Each notebook is designed to process data from uncalibrated raw FITS files to end-stage Level 3 data products (calibrated imaging mosaics, 3-D data cubes, 1-D extracted spectra, etc.).  These notebooks by default run in 'demo' mode, for which they will download and process example data drawn from the [MAST archive](https://archive.stsci.edu/).  They are, however, designed to be simple to run on arbitrary local data sets as well by configuring input directories accordingly.

These notebooks are modular, allowing users to enable or disable different stages of processing.  Likewise, they provide examples of how to customize pipeline processing for specific science cases.

The following table summarizes the notebooks currently available and the JWST [pipeline versions](https://jwst-docs.stsci.edu/jwst-science-calibration-pipeline/jwst-operations-pipeline-build-information) that they have been tested with:

| Instrument | Observing Mode | JWST Build | ``jwst`` version | Notes                                         |
|------------|----------------|------------|--------------------------|-----------------------------------------------|
| MIRI       | Imaging        | 11.2       | 1.17.1 | [JDox mode overview](https://jwst-docs.stsci.edu/jwst-mid-infrared-instrument/miri-observing-modes/miri-imaging)  |
| MIRI       | Imaging TSO    | 11.2       | 1.17.1 | [JDox mode overview](https://jwst-docs.stsci.edu/jwst-mid-infrared-instrument/miri-observing-modes/miri-time-series-observations/miri-imaging-tsos)  |
| MIRI       | LRS Slit       | 11.2       | 1.17.1 | [JDox mode overview](https://jwst-docs.stsci.edu/jwst-mid-infrared-instrument/miri-observing-modes/miri-low-resolution-spectroscopy)  |
| MIRI       | LRS Slitless   | 11.2       | 1.17.1 | [JDox mode overview](https://jwst-docs.stsci.edu/jwst-mid-infrared-instrument/miri-observing-modes/miri-time-series-observations/miri-lrs-tsos)  |
| MIRI       | MRS            | 11.2       | 1.17.1 | [JDox mode overview](https://jwst-docs.stsci.edu/jwst-mid-infrared-instrument/miri-observing-modes/miri-medium-resolution-spectroscopy)  |
| NIRCam     | Coronagraphy   | 11.2       | 1.17.1 | [JDox mode overview](https://jwst-docs.stsci.edu/jwst-near-infrared-camera/nircam-observing-modes/nircam-coronagraphic-imaging)  |
| NIRCam     | Imaging        | 11.2       | 1.17.1 | [JDox mode overview](https://jwst-docs.stsci.edu/jwst-near-infrared-camera/nircam-observing-modes/nircam-imaging)  |
| NIRISS     | Imaging        | 11.2       | 1.17.1 | [JDox mode overview](https://jwst-docs.stsci.edu/jwst-near-infrared-imager-and-slitless-spectrograph/niriss-observing-modes/niriss-imaging)  |
| NIRSpec    | BOTS           | 11.2       | 1.17.1 | [JDox mode overview](https://jwst-docs.stsci.edu/jwst-near-infrared-spectrograph/nirspec-observing-modes/nirspec-bright-object-time-series-spectroscopy)  |
| NIRSpec    | Fixed Slit     | 11.2       | 1.17.1 | [JDox mode overview](https://jwst-docs.stsci.edu/jwst-near-infrared-spectrograph/nirspec-observing-modes/nirspec-fixed-slits-spectroscopy)  |
| NIRSpec    | IFU            | 11.2       | 1.17.1 | [JDox mode overview](https://jwst-docs.stsci.edu/jwst-near-infrared-spectrograph/nirspec-observing-modes/nirspec-ifu-spectroscopy)  |
| NIRSpec    | MOS            | 11.2       | 1.17.1 | [JDox mode overview](https://jwst-docs.stsci.edu/jwst-near-infrared-spectrograph/nirspec-observing-modes/nirspec-multi-object-spectroscopy)  |

## Reference Files

As of October 2024, the JWST pipeline will automatically select the best reference file context appropriate to each pipeline version by default.  The notebooks provided here allow users to override this default if desired and choose specific contexts instead.  See [Choosing a Context](https://jwst-docs.stsci.edu/jwst-science-calibration-pipeline#JWSTScienceCalibrationPipeline-crds_contextChoosingacontext) for guidance.

## Installation

### Individual Notebooks

For advanced users, these notebooks can be downloaded individually from the GitHub repository and run in any python environment in which the [``jwst``](https://github.com/spacetelescope/jwst) package meeting the indicated minimum version has been installed.  Note that some notebooks have additional dependencies (e.g., [jdaviz](https://github.com/spacetelescope/jdaviz/)) as given in the associated requirements files.

### Package Installation

If desired, you can also clone the entire ``jwst-pipeline-notebooks`` repository to your local computer and set up a new virtual or conda environment
to avoid version conflicts with other packages you may have installed, for example:

    conda create -n jpnb python=3.11
    conda activate jpnb
    git clone https://github.com/spacetelescope/jwst-pipeline-notebooks.git

Next, move into the directory of the notebook you want to install and set up the requirements:

    cd jwst-pipeline-notebooks/notebooks/<whatever-notebook>
    pip install -r requirements.txt
    jupyter notebook

We recommend setting up a new environment for each notebook to ensure that there are no conflicting dependencies.

## Help

If you uncover any issues or bugs, you can open an issue on GitHub. For faster responses, however, we encourage you to submit a [JWST Help Desk Ticket](jwsthelp.stsci.edu)
