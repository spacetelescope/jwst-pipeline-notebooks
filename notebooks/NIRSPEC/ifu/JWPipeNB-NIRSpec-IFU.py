#!/usr/bin/env python
# coding: utf-8

# <img style="float: center;" src='https://github.com/spacetelescope/jwst-pipeline-notebooks/raw/main/_static/stsci_header.png' alt="stsci_logo" width="900px"/> 

# # NIRSpec IFU Pipeline Notebook

# **Authors**: Kayli Glidic (kglidic@stsci.edu), Maria Pena-Guerrero (pena@stsci.edu), Leonardo Ubeda (lubeda@stsci.edu); NIRSpec branch<br>
# **Last Updated**: January 7, 2025 </br>
# **Pipeline Version**: 1.16.0 (Build 11.1, Context jwst_1298.pmap)
# 
# **Purpose**:<br>
# End-to-end calibration with the James Webb Space Telescope (JWST) pipeline is divided into three main processing stages. This notebook provides a framework for processing generic Near-Infrared Spectrograph (NIRSpec) fixed slit (FS) data through [stages 1-3 of the JWST pipeline](https://jwst-docs.stsci.edu/jwst-science-calibration-pipeline/stages-of-jwst-data-processing#gsc.tab=0), including how to use associations for multi-exposure observations and how to interact and work with JWST datamodels. Data is assumed to be organized into three folders: science, background, and associations, as specified in the paths set up below. In most cases, editing cells outside the [Configuration](#1.-Configuration) section is unnecessary unless the standard pipeline processing options or plot parameters need to be modified.
# 
# **[Data](#3.-Demo-Mode-Setup-(ignore-if-not-using-demo-data))**:<br>
# This notebook is set up to use observations of Tarantula Nebula with the G140H, G235H, and G395H grisms obtained by Proposal ID (PID) 2729, Observation 5. This observation has a CYCLING dither pattern with 8 points. These observations do not include a nod or background. The demo data will automatically download unless disabled (i.e., to use local files instead).
# 
# **[JWST pipeline version and CRDS context](#Set-CRDS-Context-and-Server)**:<br>
# This notebook was written for the above-specified pipeline version and associated build context for this version of the JWST Calibration Pipeline. Information about this and other contexts can be found in the JWST Calibration Reference Data System (CRDS [server](https://jwst-crds.stsci.edu/)). If you use different pipeline versions, please refer to the table [here](https://jwst-crds.stsci.edu/display_build_contexts/) to determine what context to use. To learn more about the differences for the pipeline, read the relevant [documentation](https://jwst-docs.stsci.edu/jwst-science-calibration-pipeline/jwst-operations-pipeline-build-information#references).<br>
# 
# Please note that pipeline software development is a continuous process, so results in some cases may be slightly different if a subsequent version is used. **For optimal results, users are strongly encouraged to reprocess their data using the most recent pipeline version and [associated CRDS context](https://jwst-crds.stsci.edu/display_build_contexts/), taking advantage of bug fixes and algorithm improvements.**
# Any [known issues](https://jwst-docs.stsci.edu/known-issues-with-jwst-data/nirspec-known-issues/nirspec-mos-known-issues#NIRSpecFSKnownIssues-Resamplingof2-Dspectra&gsc.tab=0:~:text=MOS%20Known%20Issues-,NIRSpec%20MOS%20Known%20Issues,-Known%20issues%20specific) for this build are noted in the notebook.
# 
# **Updates**:<br>
# This notebook is regularly updated to incorporate the latest pipeline improvements. Find the most up-to-date version of this notebook [here](https://github.com/spacetelescope/jwst-pipeline-notebooks/).
# 
# **Recent Changes**:</br>
# * October 15, 2024: Converted notebook to follow standard template. </br>
# * November 4, 2024: Notebook updated to JWST pipeline version 1.16.0 (Build 11.1rc1).
# * January 7, 2025: Add handling for background and CRDS
# ---

# ## Table of Contents
# * [1. Configuration](#1.-Configuration)
# * [2. Package Imports](#2.-Package-Imports)
# * [3. Demo Mode Setup](#3.-Demo-Mode-Setup-(ignore-if-not-using-demo-data))
# * [4. Directory Setup](#4.-Directory-Setup)
# * [5. Stage 1: `Detector1Pipeline` (`calwebb_detector1`)](#5.-Stage-1:-Detector1Pipeline-(calwebb_detector1))
#     * [5.1 Configure `Detector1Pipeline`](#5.1-Configure-Detector1Pipeline)
#     * [5.2 Run `Detector1Pipeline`](#5.2-Run-Detector1Pipeline)
# * [6. Stage 2: `Spec2Pipeline` (`calwebb_spec2`)](#5.-Stage-2:-Spec2Pipeline-(calwebb_spec2))
#     * [6.1 Configure `Spec2Pipeline`](#6.1-Configure-Spec2Pipeline)
#     * [6.2 Create `Spec2Pipeline` ASN Files](#6.2-Create-Spec2Pipeline-ASN-Files)
#     * [6.3 Run `Spec2Pipeline`](#6.3-Run-Spec2Pipeline)
# * [7. Stage 3: `Spec3Pipeline` (`calwebb_spec3`)](#5.-Stage-3:-Spec3Pipeline-(calwebb_spec3))
#     * [7.1 Configure `Spec3Pipeline`](#7.1-Configure-Spec3Pipeline)
#     * [7.2 Create `Spec3Pipeline` ASN Files](#7.2-Create-Spec3Pipeline-ASN-Files)
#     * [7.3 Run `Spec3Pipeline`](#7.3-Run-Spec3Pipeline)
# * [8. Visualize the data](#8.-Visualize-the-data)
#     * [8.1 Display `Detector1Pipeline` Products](#8.1-Display-Detector1Pipeline-Products)
#     * [8.2 Display `Spec2Pipeline` Products](#8.2-Display-Spec2Pipeline-Products)
#     * [8.3 Display `Spec3Pipeline` Products](#8.3-Display-Spec3Pipeline-Products)
# * [9. Modifying the EXTRACT1D Reference File (as needed)](#9.-Modifying-the-EXTRACT1D-Reference-File-(as-needed))

# ## 1. Configuration
# #### Install dependencies and parameters
# To make sure that the pipeline version is compatabile with the steps discussed below and the required dependencies and packages are installed, you can create a fresh conda environment and install the provided requirements.txt file before starting this notebook:
# 
#     conda create -n nirspec_fs_pipeline python=3.12
#     conda activate nirspec_fs_pipeline
#     pip install -r requirements.txt
# 
# Set the basic parameters to configure the notebook. These parameters determine what data gets used, where data is located (if already on disk), and the type of background subtraction (if any). The list of parameters includes:
# 
# * `demo_mode`:
#     * `True`: Downloads example data from the [Barbara A. Mikulski Archive for Space Telescopes (MAST)](https://archive.stsci.edu/) and processes it through the pipeline. All processing will occur in a local directory unless modified in [Section 3](#3.-Demo-Mode-Setup-(ignore-if-not-using-demo-data)) below.
#     * `False`: Process your own downloaded data; provide its location.
# * **Directories with data**:
#     * `sci_dir`: Directory where science observation data is stored.
#     * `bg_dir`: Directory where background observation data is stored.
#     * `asn_dir`: Directory where Stage 2/3 associations are stored.
# * **[Backgroud subtraction methods](https://jwst-pipeline.readthedocs.io/en/latest/jwst/background_subtraction/main.html#spectroscopic-modes:~:text=the%20calwebb_image3%20pipeline.-,Spectroscopic%20Modes,%EF%83%81,-Spectroscopic%20observations%20allow)** (`True` = run, `False` = skip):
#     * `master_bg`: Apply master-background subtraction in `calwebb_spec3`?
#     * `pixel_bg`: Apply pixel-to-pixel background subtraction in `calwebb_spec2`?
# * **Compare with MAST products** (`compare_mast`): Compare latest reductions to data products from the MAST archive?
# 

# In[1]:


# Basic import necessary for configuration.

import os
import warnings
import logging

# Control logging level: INFO, WARNING, ERROR
# Run command loging.disable if want to hide logging
# ERROR messages.
#logging.disable(logging.ERROR)
warnings.simplefilter("ignore", RuntimeWarning)


# <div class="alert alert-block alert-warning">
#     
# Note that `demo_mode` must be set appropriately below.
# </div>

# In[ ]:


# Set parameters for demo_mode, data mode directories, and processing steps.

# -------------------------------DEMO MODE-----------------------------------
demo_mode = True

if demo_mode:
    print('Running in demonstration mode using online example data!')

# ----------------------------User Mode Directories--------------------------
else:  # If demo_mode = False, look for user data in these paths.

    # Set directory paths for processing specific data; adjust to your local
    # directory setup (examples provided below).
    basedir = os.path.join(os.getcwd(), '')

    # Directory to science observation data; expects uncalibrated data in
    # sci_dir/uncal/ and results in stage1, stage2, and stage3 directories.
    sci_dir = os.path.join(basedir, 'ifu_data_02729/Obs005', '')

    # Directory to background observation data; expects uncalibrated data in
    # bg_dir/uncal/ and results in stage1, stage2, and stage3 directories.
    # bg_dir = os.path.join(basedir, 'ifu_data_02729/Obs002', '')
    bg_dir = ''  # If no background observation, use an empty string.

    # Directory to stage 2/3 association files.
    asn_dir = os.path.join(basedir, 'asn', '')

# ---------------------------Set Processing Steps----------------------------
# Individual pipeline stages can be turned on/off here.  Note that a later
# stage won't be able to run unless data products have already been
# produced from the prior stage.

# Science processing
dodet1 = True  # calwebb_detector1
dospec2 = True  # calwebb_image2
dospec3 = True  # calwebb_image3
doviz = True  # Visualize calwebb outputs

# Background Processing
dodet1bg = False  # calwebb_detector1
dospec2bg = False # calwebb_spec2 (needed for Master Background subtraction)

# How should background subtraction using any dedicated backgrounds be done?
# If none are selected, data will not be background subtracted.
# pixel_bg - True for noded observationd
master_bg = False  # Master-background subtraction in spec3.
pixel_bg = False  # Pixel-based background subtraction in spec2. 


# ---
# 
# ### Set CRDS Context and Server
# Before importing `CRDS` and `JWST` modules, we need to configure our environment. This includes defining a CRDS cache directory in which to keep the reference files that will be used by the calibration pipeline. If the local CRDS cache directory has not been set, it will automatically be created in the home directory.<br><br>
# [Build Context Table](https://jwst-crds.stsci.edu/display_build_contexts/)

# In[ ]:


# ------------------------Set CRDS context and paths------------------------# Each version of the calibration pipeline is associated with a specific CRDS
# context file. The pipeline will select the appropriate context file behind
# the scenes while running. However, if you wish to override the default context
# file and run the pipeline with a different context, you can set that using
# the CRDS_CONTEXT environment variable. Here we show how this is done,
# although we leave the line commented out in order to use the default context.
# If you wish to specify a different context, uncomment the line below.
#os.environ['CRDS_CONTEXT'] = 'jwst_1298.pmap'  # CRDS context for 1.16.0

# Set CRDS cache directory to user home if not already set.
if os.getenv('CRDS_PATH') is None:
    os.environ['CRDS_PATH'] = os.path.join(os.path.expanduser('~'), 'crds_cache')

# Check whether the CRDS server URL has been set. If not, set it.
if os.getenv('CRDS_SERVER_URL') is None:
    os.environ['CRDS_SERVER_URL'] = 'https://jwst-crds.stsci.edu'

# Output the current CRDS path and server URL in use.
print('CRDS local filepath:', os.environ['CRDS_PATH'])
print('CRDS file server:', os.environ['CRDS_SERVER_URL'])


# ---
# 
# ## 2. Package Imports
# 

# In[ ]:


# Use the entire available screen width for this notebook.
from IPython.display import display, HTML, JSON
display(HTML("<style>.container { width:95% !important; }</style>"))


# In[5]:


# ----------------------General Imports----------------------
import time
import copy
import glob
import json
import asdf
import itertools
import numpy as np
from pprint import pprint

# ----------------------Astropy Imports----------------------
# Astropy utilities for opening FITS files, downloading demo files, etc.
from astropy.io import fits
from astropy.wcs import WCS
from astropy.stats import sigma_clip
from astropy.visualization import ImageNormalize, ManualInterval, LogStretch
from astropy.visualization import LinearStretch, AsinhStretch, simple_norm

# -------------------- Astroquery Imports ----------------------
from astroquery.mast import Observations

# ----------------------Plotting Imports---------------------
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib import gridspec as grd
from matplotlib.patches import Rectangle, Circle
from matplotlib.collections import PatchCollection


# <div class="alert alert-block alert-info">
# 
# Installation instructions for the JWST pipeline found here: [JDox](https://jwst-docs.stsci.edu/jwst-science-calibration-pipeline-overview) •
# [ReadtheDocs](https://jwst-pipeline.readthedocs.io) •
# [Github](https://github.com/spacetelescope/jwst)
# 
# </div>

# In[ ]:


# ----------------------JWST Calibration Pipeline Imports----------------------
import jwst  # Import the base JWST and CRDS packages.
import crds
from crds.client import api
from stpipe import crds_client

# JWST pipelines (each encompassing many steps).
from jwst.pipeline import Detector1Pipeline  # calwebb_detector1
from jwst.pipeline import Spec2Pipeline  # calwebb_spec2
from jwst.pipeline import Spec3Pipeline  # calwebb_spec3
from jwst.extract_1d import Extract1dStep  # Extract1D Step
from jwst import datamodels  # JWST pipeline utilities: datamodels.

print("JWST Calibration Pipeline Version = {}".format(jwst.__version__))
print("Using CRDS Context = {}".format(crds.get_context_name('jwst')))


# ---
# 
# ### Define Convience Functions

# Define a function to update an existing association file so the expname field is the abslute path to the file.

# In[7]:


def update_asn_paths(asn_files,
                     exclude_dirs=[]):
    """
    Update the expname field in an ASN file with its absolute path.

    The absolute path is determined by locating matching files in the
    current directory while excluding any files found in the specified
    excluded directories. Absolute paths ensure that the pipeline correctly
    locates the files, regardless of the ASN file's location.

    Parameters
    ----------
    asn_files : list of str
        List of ASN files to update.
    exclude_dirs : list of str, optional
        List of directories to exclude in the search.

    Returns
    -------
    None.
    """

    # Ensure asn_files is a list.
    asn_files = [asn_files] if isinstance(asn_files, str) else asn_files

    # Set up logging.
    logging.basicConfig(level=logging.INFO)

    for asn in asn_files:
        try:
            with open(asn, 'r') as file:
                data = json.load(file)
        except Exception as e:
            logging.error(f"Error reading file {asn}: {e}")
            continue  # Skip this file if it can't be read

        update = False

        # Loop through each product and its members.
        for product in data['products']:
            for member in product['members']:
                search_pattern = f"**/{member['expname']}"
                filtered_files = [f for f in glob.glob(os.path.join(os.getcwd(),
                                  search_pattern), recursive=True) if not
                                  any(f.startswith(exc) for exc in exclude_dirs)]
                if len(filtered_files) > 0:
                    member['expname'] = filtered_files[0]
                    update = True

        basn = os.path.basename(asn)
        if update:
            try:
                with open(asn, 'w') as json_file:
                    json.dump(data, json_file, indent=4)
                logging.info(f"{basn} 'expname' paths have been updated to absolute paths!")
            except Exception as e:
                logging.error(f"Error saving updated file {asn}: {e}")
        else:
            logging.info(f"{basn} 'expname' paths NOT updated! Paths may be absolute.")


# In[8]:


# Print out the time benchmark
time0 = time.perf_counter()


# ---
# ## 3. Demo Mode Setup (ignore if not using demo data)
# <div class="alert alert-block alert-info">
# 
# The data in this notebook is public and does not require a token. For other data sets, you may need to provide a token. For more infomation visit the
# [astroquery](https://astroquery.readthedocs.io/en/latest/index.html) documentation.
# 
# </div>
# 
# 
# If running in demonstration mode, set up the program information to retrieve the uncalibrated data (`_uncal.fits`) automatically from MAST using `astroquery`. MAST provides flexibility by allowing searches based on proposal ID and observation ID, rather than relying solely on filenames. More information about the JWST file naming conventions can be found [here](https://jwst-pipeline.readthedocs.io/en/latest/jwst/data_products/file_naming.html).
# 
# The IFU demo data in this notebook is from the [Early Release Science (ERS) Proposal ID 2729](https://www.stsci.edu/jwst/science-execution/program-information?id=2729) and features observations of the Tarantula Nebula (extended source) using multiple grisms. The program setup is briefly summarized in the table below.
# 
# | Demo Target: Tarantula Nebula | | |
# |:-----------:|:-------:|:---:|
# | Proposal ID | 02729 | Program number |
# | OBSERVTN | 005 | Observation number |
# | [GRATING/FILTER](https://jwst-docs.stsci.edu/jwst-near-infrared-spectrograph/nirspec-observing-modes/nirspec-ifu-spectroscopy) | G140H/F100LP | λ: 0.97–1.89 μm (a medium resolution, R ~ 1000) |
# |                | G235H/F170LP | λ: 1.66–3.17 μm (a high resolution, R ~ 2700) |
# |                | G395H/F290LP | λ: 2.87–5.27 μm (a high resolution, R ~ 2700) |
# | SUBARRAY | SUBS200A1 | Subarray used |
# | NINTS | 2 | Number of integrations in exposure |
# | NGROUPS | 30 | Number of groups in integration |
# |   DURATION  | 87.533 [s] | Total duration of one exposure |
# |   READPATT  | NRSIRS2RAPID | Readout Pattern |
# |   PATTTYPE  | CYCLING | Primary dither pattern type |
# |   PATTSIZE  | LARGE | Primary dither pattern size (1.0" extent) |
# |   NUMDTHPT  | 8 | Total number of points in pattern |
# |   SRCTYAPT  | UNKNOWN | Source Type selected in APT |
# 
# > **Note:** The presence of a physical gap between detectors affects high-resolution IFU observations because the spectra are long enough to span both NIRSpec detectors. When using the grating-filter combination G140H/F070LP (or PRISM/CLEAR) the resulting spectra do not have any gaps because the spectra do not extend beyond NRS1. [More Info ...](https://jwst-docs.stsci.edu/jwst-near-infrared-spectrograph/nirspec-operations/nirspec-ifu-operations/nirspec-ifu-wavelength-ranges-and-gaps#NIRSpecIFUWavelengthRangesandGaps-Wavelengthgaps)

# In[ ]:


# Print out the time benchmark
time1 = time.perf_counter()
print(f"Runtime so far: {time1 - time0:0.4f} seconds")


# In[ ]:


# Set up the program information for demo mode.

if demo_mode:

    print('Running in demonstration mode. '
          'Example data will be downloaded from MAST!')

    # NOTE:
    # The data in this notebook is public and does not require a token.
    # For other data sets, you may need to provide a token.
    # Observations.login(token=None)

    # --------------Program and observation information--------------
    program = "02729"
    sci_observtn = "005"
    bg_observtn = None
    # Possible filter options [#"F100LP;G140H",#"F170LP;G235H","F290LP;G395H"]
    # Limiting selection to one
    filters = ["F290LP;G395H"]
    
    # ----------Define the base and observation directories----------
    basedir = os.path.join('.', f'ifu_data_{program}')
    sci_dir = os.path.join(basedir, f'Obs{sci_observtn}')
    bg_dir = os.path.join(basedir, f'Obs{bg_observtn}') if bg_observtn else ''
    asn_dir = os.path.join(basedir, 'asn/')
    uncal_dir = os.path.join(sci_dir, 'uncal/')
    uncal_bgdir = os.path.join(bg_dir, 'uncal/') if bg_observtn else ''

    os.makedirs(uncal_dir, exist_ok=True)
    os.makedirs(asn_dir, exist_ok=True)
    if bg_observtn:
        os.makedirs(uncal_bgdir, exist_ok=True)


# Click on the following links to learn more about querying and downloading data:<br>
# • [Downloading data](https://astroquery.readthedocs.io/en/latest/mast/mast_obsquery.html#downloading-data)<br>
# • [Observations Class](https://astroquery.readthedocs.io/en/latest/api/astroquery.mast.ObservationsClass.html)<br>
# • [Products Field Descriptions](https://mast.stsci.edu/api/v0/_productsfields.html)<br><br>
# Identify the list of science (sci) data to download from MAST.

# In[11]:


# Obtain a list of observation IDs for the specified demo program.

if demo_mode:
    # --------------------SCIENCE Observation--------------------
    sci_obs_id_table = Observations.query_criteria(instrument_name=['NIRSPEC/IFU'],
                                                   provenance_name=["CALJWST"],
                                                   obs_id=[f'*{program}*{sci_observtn}*'])

    # ------------------BACKGROUND Observation-------------------
    if bg_observtn:
        bg_obs_id_table = Observations.query_criteria(instrument_name=['NIRSPEC/IFU'],
                                                      provenance_name=["CALJWST"],
                                                      obs_id=[f'*{program}*{bg_observtn}*'])


# The demo dataset consists of eight `_uncal.fits` files (per detector), each approximately 63 MB in size. Here we will identify the SCI, BKG, and association files to download.

# In[ ]:


# Convert visits into a list of uncalibrated data and ASN files.

if demo_mode:
    file_criteria = {'filters': filters, 'calib_level': [1],
                     'productSubGroupDescription': 'UNCAL'}
    asn_criteria = {'filters': filters, 'calib_level': [2, 3],
                    'productSubGroupDescription': 'ASN'}

    # Initialize lists for science, background, and ASN files.
    sci_downloads, bg_downloads, asn_downloads = [], [], []

    pfilter = Observations.filter_products  # Alias for filter_products method.

    # ----------Identify uncalibrated SCIENCE files associated with each visit----------
    for exposure in sci_obs_id_table:
        sci_products = Observations.get_product_list(exposure)
        asn_downloads.extend(pfilter(sci_products, **asn_criteria)['dataURI'])

        # Filter for full-size science files (exclude smaller confirmation images).
        avg_sci_size = np.nanmean(sci_products['size'])
        sci_products = sci_products[sci_products['size'] > avg_sci_size]
        sci_downloads.extend(pfilter(sci_products, **file_criteria)['dataURI'])

    # Filter for full-size background files (exclude smaller confirmation images).
    if bg_observtn:
        for exposure in bg_obs_id_table:
            bg_products = Observations.get_product_list(exposure)
            asn_downloads.extend(pfilter(bg_products, **asn_criteria)['dataURI'])

            avg_bg_size = np.nanmean(bg_products['size'])
            bg_products = bg_products[bg_products['size'] > avg_bg_size]
            bg_downloads.extend(pfilter(bg_products, **file_criteria)['dataURI'])

    # Filter out other observations and remove duplicates.
    sci_downloads = {f for f in sci_downloads if f"jw{program}{sci_observtn}" in f}
    asn_downloads = {f for f in asn_downloads if any(f"-{p}{sci_observtn}_" in f
                                                     for p in ["o", "c?"])}
    
    if bg_observtn:
        bg_downloads = {f for f in bg_downloads if f"jw{program}{bg_observtn}" in f}
        print(f"Background files selected for downloading: {len(bg_downloads)}")
    else:
        print(f"Background files selected for downloading: 0")

    print(f"Science files selected for downloading: {len(sci_downloads)}")
    print(f"ASN files selected for downloading: {len(asn_downloads)}")


# In[ ]:


# Download data and place them into the appropriate directories.

if demo_mode:
    for file in sci_downloads:
        sci_manifest = Observations.download_file(file, local_path=uncal_dir)
    for file in bg_downloads:
        bg_manifest = Observations.download_file(file, local_path=uncal_bgdir)
    for file in asn_downloads:
        asn_manifest = Observations.download_file(file, local_path=asn_dir, cache=False)


# <div class="alert alert-block alert-warning">
# 
# **Warning**: If this notebook is halted during this step, the downloaded file may be incomplete, and cause crashes later on!
# </div>

# ---
# ## 4. Directory Setup
# Set up detailed paths to input/output stages here.

# In[13]:


# Define/create output subdirectories to keep data products organized.

# -----------------------------Science Directories------------------------------
uncal_dir = os.path.join(sci_dir, 'uncal/')  # Uncalibrated pipeline inputs.
det1_dir = os.path.join(sci_dir, 'stage1/')  # calwebb_detector1 pipeline outputs.
spec2_dir = os.path.join(sci_dir, 'stage2/')  # calwebb_spec2 pipeline outputs.
spec3_dir = os.path.join(sci_dir, 'stage3/')  # calwebb_spec3 pipeline outputs.

os.makedirs(det1_dir, exist_ok=True)
os.makedirs(spec2_dir, exist_ok=True)
os.makedirs(spec3_dir, exist_ok=True)

# ---------------------------Background Directories-----------------------------
uncal_bgdir = os.path.join(bg_dir, 'uncal/')  # Uncalibrated pipeline inputs.
det1_bgdir = os.path.join(bg_dir, 'stage1/')  # calwebb_detector1 pipeline outputs.
spec2_bgdir = os.path.join(bg_dir, 'stage2/')  # calwebb_spec2 pipeline outputs.

if bg_dir:
    os.makedirs(det1_bgdir, exist_ok=True)
    os.makedirs(spec2_bgdir, exist_ok=True)

# -------------------------------MAST Directory---------------------------------
mast_products_dir = os.path.join(basedir, 'mast_products/')  # MAST products.


# In[ ]:


# Print out the time benchmark
time1 = time.perf_counter()
print(f"Runtime so far: {time1 - time0:0.4f} seconds")


# ---
# ## 5. Stage 1: `Detector1Pipeline` (`calwebb_detector1`)
# 
# In this section, we process the data through the `calwebb_detector1` pipeline to create Stage 1 [data products](https://jwst-pipeline.readthedocs.io/en/latest/jwst/data_products/science_products.html).
# 
# * **Input**: Raw exposure (`_uncal.fits`) containing original data from all detector readouts (ncols x nrows x ngroups x nintegrations).
# * **Output**: Uncalibrated countrate (slope) image in units of DN/s:
#     * `_rate.fits`: A single countrate image averaged over multiple integrations (if available).
#     * `_rateints.fits`: Countrate images for each integration, saved in multiple extensions.
# 
# The `Detector1Pipeline` applies basic detector-level corrections on a group-by-group basis, followed by ramp fitting for all exposure types, commonly referred to as "ramps-to-slopes" processing.
# 
# ---

# ### 5.1 Configure `Detector1Pipeline`
# 
# The `Detector1Pipeline` has the following steps available for NIRSpec FS:
# 
# * `group_scale` : Rescales pixel values to correct for improper onboard frame averaging.
# * `dq_init` : Initializes the data quality (DQ) flags for the input data.
# * `saturation` : Flags pixels at or below the A/D floor or above the saturation threshold.
# * `superbias` : Subtracts the superbias reference file from the input data.
# * `refpix` : Use reference pixels to correct bias drifts.
# * `linearity` : Applies a correction for non-linear detector response.
# * `dark_current` : Subtracts the dark current reference file from the input data.
# * `jump` : Performs CR/jump detection on each ramp integration within an exposure.
# * `clean_flicker_noise`: Removes flicker (1/f) noise from calibrated ramp images (similar to `nsclean` in spec2).
# * `ramp_fit` : Determines the mean count rate (counts per second) for each pixel by performing a linear fit to the input data.
# * `gain_scale` : Corrects pixel values for non-standard gain settings, primarily in NIRSpec subarray data.
# 
# For more information about each step and a full list of step arguments, please refer to the official documentation: [JDox](https://jwst-docs.stsci.edu/jwst-science-calibration-pipeline-overview/stages-of-jwst-data-processing/calwebb_detector1) •
# [ReadtheDocs](https://jwst-pipeline.readthedocs.io/en/stable/jwst/pipeline/calwebb_detector1.html)
# 
# Below, we set up a dictionary that defines how the `Detector1Pipeline` should be configured for IFU data.

# <div class="alert alert-warning">
#   To override specific steps and reference files, use the examples below.
# </div>

# In[15]:


# Set up a dictionary to define how the Detector1 pipeline should be configured.

# -------------------------Boilerplate dictionary setup-------------------------
det1dict = {}
det1dict['group_scale'], det1dict['dq_init'], det1dict['saturation'] = {}, {}, {}
det1dict['superbias'], det1dict['refpix'] = {}, {}
det1dict['linearity'], det1dict['dark_current'] = {}, {}
det1dict['jump'], det1dict['ramp_fit'], det1dict['gain_scale'] = {}, {}, {}

# ---------------------------Override reference files---------------------------

# Overrides for various reference files (example).
# Files should be in the base local directory or provide full path.
#det1dict['dq_init']['override_mask'] = 'myfile.fits' # Bad pixel mask
#det1dict['superbias']['override_superbias'] = 'myfile.fits' # Bias subtraction
#det1dict['dark_current']['override_dark'] = 'myfile.fits' # Dark current subtraction

# -----------------------------Set step parameters------------------------------

# Overrides for whether or not certain steps should be skipped (example).
det1dict['linearity']['skip'] = False  # This is the default.

# Turn on multi-core processing (off by default).
# Choose what fraction of cores to use (quarter, half, or all).
det1dict['jump']['maximum_cores'] = 'half'
#det1dict['ramp_fit']['maximum_cores'] = 'half'

# Turn on detection of cosmic ray snowballs (on by default).
det1dict['jump']['expand_large_events'] = True
det1dict['jump']['expand_factor'] = 3  # (default 2)


# <div class="alert alert-info">
# 
# Many exposures are affected by artifacts known as [snowballs](https://jwst-docs.stsci.edu/known-issues-with-jwst-data/shower-and-snowball-artifacts#gsc.tab=0) caused by large cosmic ray events. These artifacts are particularly significant in deep exposures with long integration times, with an estimated rate of one snowball per detector (FULL FRAME) per 20 seconds. To expand the number of pixels flagged as jumps around large cosmic ray events, set `expand_large_events` to True. An `expand_factor` of 3 works well for NIRSpec observations to cover most snowballs.
# </div>

# <div class="alert alert-info">
# 
# JWST detector readout electronics (a.k.a. SIDECAR ASICs) generate significant 1/f noise during detector operations and signal digitization. This noise manifests as faint banding along the detector's slow axis and varies from column to column. For NIRSpec data, the primary pipeline algorithm to address 1/f noise is `nsclean` in the `Spec2Pipeline` (Rauscher 2023) but is off by default.
# 
# An additional 1/f noise-cleaning algorithm, `clean_flicker_noise`, has been implemented at the group stage in the `Detector1Pipeline`. This step is also off by default.
# </div>

# ---
# ### 5.2 Run `Detector1Pipeline`
# 
# Run the science files and, if available, any background files through the `calwebb_detector1` pipeline using the `.call()` method.
# 
# We use `.call()` instead of `.run()` to ensure that the latest default parameters from CRDS are applied ([ReadtheDocs](https://jwst-pipeline.readthedocs.io/en/latest/jwst/stpipe/call_via_run.html)).
# 
# This stage takes approximately 14 minutes to process sixteen `_uncal.fits` files (~1 minutes per file) and generate `_rate.fits` files.

# In[ ]:


# Final list of UNCAL files ready for Stage 1 processing.
uncal_sci = sorted(glob.glob(uncal_dir + '*uncal.fits'))
print(f"Science UNCAL Files:\n{'-'*20}\n" + "\n".join(uncal_sci))

if bg_dir:
    uncal_bg = sorted(glob.glob(uncal_bgdir + '*uncal.fits'))
    print(f"Background UNCAL Files:\n{'-'*20}\n" + "\n".join(uncal_bg))


# In[ ]:


# Run Stage 1 pipeline using the custom det1dict dictionary.

start = time.time()

if dodet1:
    #--------------------------Science UNCAL files--------------------------
    for uncal_file in sorted(glob.glob(uncal_dir + '*uncal.fits')):

        print(f"Applying Stage 1 Corrections & Calibrations to: "
              f"{os.path.basename(uncal_file)}")

        det1_result = Detector1Pipeline.call(uncal_file,
                                             save_results=True,
                                             steps=det1dict,
                                             output_dir=det1_dir)
        print(f"\nRun time: {round((time.time()-start)/60.0, 1)} min")

    print("Stage 1 has been completed for SCI data\n")
else:
    print('Skipping Detector1 processing for SCI  data')


# ### Calibrating Background Files
# Look for input background files and run calwebb_detector1
# pipeline using the call method.

# In[ ]:


# Run Detector1 stage of pipeline on any background files
if dodet1bg:
    #------------------------Background UNCAL files-------------------------
    for uncal_file in sorted(glob.glob(uncal_bgdir + '*uncal.fits')):

        print(f"Applying Stage 1 Corrections & Calibrations to: "
              f"{os.path.basename(uncal_file)}")

        det1bg_result = Detector1Pipeline.call(uncal_file,
                                               save_results=True,
                                               steps=det1dict,
                                               output_dir=det1_bgdir)
        print(f"\nRun time: {round((time.time()-start)/60.0, 1)} min")

    print("Stage 1 has been completed for BKG data\n")
else:
    print('Skipping Detector1 processing for BKG data')


# In[20]:


# Print output result details:
# det1_result.__dict__  # View entire contents.
# det1_result.meta.filename
# det1_result.data.shape


# In[ ]:


# Print out the time benchmark
time1 = time.perf_counter()
print(f"Runtime so far: {time1 - time0:0.4f} seconds")


# In[ ]:


# Final list of RATE[INTS] files ready for Stage 2 processing.
rate_sci = sorted(glob.glob(det1_dir + '*_rate*.fits'))
print(f"SCIENCE | RATE[INTS] Files:\n{'-'*20}\n" + "\n".join(rate_sci))

if bg_dir:
    rate_bg = sorted(glob.glob(det1_bgdir + '*_rate*.fits'))
    print(f"BACKGROUND | RATE[INTS] Files:\n{'-'*20}\n" + "\n".join(rate_bg))


# ---
# ## 6. Stage 2: `Spec2Pipeline` (`calwebb_spec2`)
# 
# In this section, we process our countrate (slope) image products from Stage 1 (`calwebb_detector1`) through the Spec2 (`calwebb_spec2`) pipeline to create Stage 2 [data products](https://jwst-pipeline.readthedocs.io/en/latest/jwst/data_products/science_products.html).
# 
# * **Input**: A single countrate (slope) image (`_rate[ints].fits`) or an association file listing multiple inputs.
# * **Output**: Calibrated products (rectified and unrectified) and 1D spectra.
#     * `_cal[ints].fits`: Calibrated 2D (unrectified) spectra (ncols x nrows).
# 	* `_s3d.fits`: Resampled 3D IFU cube (ncols x nrows x nwaves).
# 	* `_x1d[ints].fits`: Extracted 1D spectroscopic data (wavelength vs. flux).
# 
# In Stage 2, each exposure (or association) and detector produces a single file, with multiple extensions corresponding to each source.
# 
# The `Spec2Pipeline` applies additional instrumental corrections and calibrations (e.g., slit loss, path loss, etc.,) to countrate products that result in a fully calibrated individual exposure (per nod/dither position). The `Spec2Pipeline` also converts countrate products from units of DN/s to flux (Jy) for point sources and surface brightness (MJy/sr) for extended sources.
# 
# <div class="alert alert-info">
# Note there has been a bug in the `cube_build` step that caused the point source flux to not be conserved when using different spatial sampling. A fix has been implemented as of release DMS build 9.3/CAL_VER 1.10.2. In order to enable the correct functionality, the units of the `_cal.fits` files and cubes will now be in surface brightness, and only the 1D extracted spectra will be in units of Jy.
# </div>
# 
# ---

# ### 6.1 Configure `Spec2Pipeline`
# The `Spec2Pipeline` has the following steps available for NIRSpec FS:
# 
# * `assign_wcs`: Assigns wavelength solution for spectra.
# * `msaflagopen`: Flags pixels in NIRSpec exposures affected by MSA shutters stuck in the open position.
# * `nsclean`: Cleans 1/f noise.
# * `imprint`: Removes patterns caused by the MSA structure in NIRSpec MOS and IFU exposures.
# * `bkg_subtract`: Performs image subtraction for background removal.
# * `srctype`: Determines whether a spectroscopic source should be classified as a point or extended object.
# * `flat_field`: Applies flat-field corrections to the input science dataset.
# * `pathloss`: Calculates and applies corrections for signal loss in spectroscopic data.
# * `photom`: Applies photometric calibrations to convert data from countrate to surface brightness or flux density.
# * `pixel_replace`: Interpolates and estimates flux values for pixels flagged as DO_NOT_USE in 2D extracted spectra.
# * `cube_build`: Produces 3D spectral cubes.
# * `extract_1d`: Extracts a 1D signal from 2D or 3D datasets.
# 
# For more information about each step and a full list of step arguments, please refer to the official documentation: [JDox](https://jwst-docs.stsci.edu/jwst-science-calibration-pipeline-overview/stages-of-jwst-data-processing/calwebb_spec2) •
# [ReadtheDocs](https://jwst-pipeline.readthedocs.io/en/latest/jwst/pipeline/calwebb_spec2.html)
# 
# Below, we set up a dictionary that defines how the `Spec2Pipeline` should be configured for IFU data.

# <div class="alert alert-warning">
# 
# If pixel-to-pixel background subtraction was chosen above, it will be applied during this stage.</br>
# To override specific steps and reference files, use the examples below. 
# 
# </div>

# In[23]:


time_spec2 = time.perf_counter()


# In[24]:


# Set up a dictionary to define how the Spec2 pipeline should be configured.

# -------------------------Boilerplate dictionary setup-------------------------
spec2dict = {}
spec2dict['assign_wcs'], spec2dict['msa_flagging'] = {}, {}
spec2dict['nsclean'], spec2dict['imprint_subtract'] = {}, {}
spec2dict['bkg_subtract'] = {}
spec2dict['srctype'], spec2dict['wavecorr'] = {}, {}
spec2dict['flat_field'], spec2dict['pathloss'] = {}, {}
spec2dict['photom'], spec2dict['pixel_replace'] = {}, {}
spec2dict['cube_build'], spec2dict['extract_1d'] = {}, {}

# ---------------------------Override reference files---------------------------

# Overrides for various reference files (example).
# Files should be in the base local directory or provide full path.
#spec2dict['extract_1d']['override_extract1d'] = 'myfile.json'

# -----------------------------Set step parameters------------------------------

# Overrides for whether or not certain steps should be skipped (example).
spec2dict['bkg_subtract']['skip'] = not pixel_bg
spec2dict['imprint_subtract']['skip'] = False

# Run pixel replacement code to extrapolate values for otherwise bad pixels
# This can help mitigate 5-10% negative dips in spectra of bright sources.
# Use the 'fit_profile' algorithm.
#spec2dict['pixel_replace']['skip'] = False
#spec2dict['pixel_replace']['n_adjacent_cols'] = 5
#spec2dict['pixel_replace']['algorithm'] = 'fit_profile'

# Run nsclean for 1/f noise.
#spec2dict['nsclean']['skip'] = False
#spec2dict['nsclean']['n_sigma'] = 2


# <div class="alert alert-info">
# 
# To correct for 1/f noise with `nsclean` in Stage 2, see the demo notebook for IFU data [here](https://github.com/spacetelescope/jdat_notebooks/tree/main/notebooks/NIRSpec/NIRSpec_NSClean).
# 
# </div>

# ---
# ### 6.2 `Spec2Pipeline` ASN Files
# 
# [Association (ASN) files](https://jwst-pipeline.readthedocs.io/en/stable/jwst/associations/overview.html) define the relationships between multiple exposures, allowing them to get processed as a set rather than individually. Processing an ASN file enables the exposures to be calibrated, archived, retrieved, and reprocessed as a set rather than as individual objects.
# 
# [Stage 2 ASN files](https://jwst-pipeline.readthedocs.io/en/latest/jwst/associations/level2_asn_technical.html) for IFU data can include `science`, `background`, and `imprint` exposure types. A Stage 2 ASN file requires at least one `science` file but can contain multiple `background` and `imprint` (leakcals) files that enable pixel-to-pixel background subtraction and imprint subtraction in `calwebb_spec2`.
# 
# This notebook downloads Stage 2 ASN files directly from MAST. However, the downloaded ASN files expect the input files to be in the same directory, which is incompatible with our directory structure. In the cell below, we update the `expname` fields in the ASN files to use absolute paths to ensure the pipeline looks in the correct locations.
# 
# <div class="alert alert-block alert-warning">
# 
# Background subtraction may not be correctly applied if more than *one* `science` file is included in the association. Additionally, pixel-to-pixel background subtraction will only be performed if the grating wheel has not moved between the target and off-scene associated background exposures. If the grating wheel moved between the target and background exposures (as would be the case if they were in different visits), pipeline processing will follow a more involved "master background" subtraction done in Stage 3.
# 
# </div>

# In[ ]:


# Get list of all spec2 ASN files and categorize them.
spec2_asn_all = glob.glob(f"{asn_dir}*spec2*asn.json")
candidate_asn = [asn for asn in spec2_asn_all if "-c" in asn]
obs_asn = [asn for asn in spec2_asn_all if "-o" in asn]

# Choose ASN files: candidate if available, otherwise observation ASN.
spec2_asn = candidate_asn or obs_asn
print(f"Stage 2 ASN Files:\n{'-'*20}\n" + "\n".join(spec2_asn))


# In[26]:


# Convert 'expname' paths in the ASN file to absolute paths.
# Ensures the pipeline can locate the files,
# regardless of the ASN file's location.
update_asn_paths(spec2_asn, exclude_dirs=[mast_products_dir])


# In[ ]:


# Open an ASN file as an example.
# Check that file paths have been correctly updated.
with open(spec2_asn[0], 'r') as f_obj:
    asnfile_data = json.load(f_obj)

JSON(asnfile_data, expanded=True)


# ---
# ### 6.3 Run `Spec2Pipeline`
# 
# Run the science files and, if available, any background files through the `calwebb_spec2` pipeline using the `.call()` method.

# <div class="alert alert-block alert-warning">
# Perform pixel-to-pixel background subtraction (if desired) here in Stage 2. Otherwise, reduce the backgrounds individually for master background subtraction in Stage 3 (if desired).
# </div>

# In[28]:


# To save on runtime, make a new version of our spec2 parameter dictionary
# that turns off creation of quicklook 2d/1d spectra for science data.
spec2dict_sci = copy.deepcopy(spec2dict)
spec2dict_sci['cube_build']['skip'] = False  # S2D products.
spec2dict_sci['extract_1d']['skip'] = False  # X1D products.


# In[ ]:


# Run Stage 2 pipeline using the custom spec2dict dictionary.

start = time.time()

if dospec2:
    # --------------------------Science ASN files--------------------------
    for asn in spec2_asn:

        asn_data = json.load(open(asn))
        sci_file = os.path.basename(asn_data['products'][0]['members'][0]['expname'])
        print(f"Applying Stage 2 Corrections & Calibrations to: {sci_file}")

        spec2sci_result = Spec2Pipeline.call(asn,
                                             save_results=True,
                                             steps=spec2dict_sci,
                                             output_dir=spec2_dir)
        print(f"\nRun time: {round((time.time()-start)/60.0, 1)} min")
        print("Stage 2 has been completed for SCI data!\n")


# Prepare background files for master background subtraction in Stage 3

# In[ ]:


# ------------------------Background RATE files------------------------
if dospec2bg & master_bg:

   for rate in rate_bg:
       print(f"Applying Stage 2 Corrections & Calibrations to: "
             f"{os.path.basename(rate)}")

       spec2bg_result = Spec2Pipeline.call(rate,
                                           save_results=True,
                                           steps=spec2dict,
                                           output_dir=spec2_bgdir)
       print(f"\nRun time: {round((time.time()-start)/60.0, 1)} min")
       print("Stage 2 has been completed for BKG data\n")
   else:
       print("Skipping Stage 2 for BKG data \n")

else:
   print("Skipping Stage 2 for SCI and BKG data \n")


# In[ ]:


# Print out the time benchmark
time1 = time.perf_counter()
print(f"Runtime so far: {time1 - time0:0.4f} seconds")
print(f"Runtime for Spec2: {time1 - time_spec2} seconds")


# In[33]:


# Print output result details:
# spec2sci_result.__dict__  # View entire contents.
# spec2sci_result.meta.filename
# spec2sci_result.data.shape


# In[ ]:


# List the Stage 2 products.

# -----------------------------Science files-----------------------------
sci_cal = sorted(glob.glob(spec2_dir + '*_cal.fits'))
sci_s3d = sorted(glob.glob(spec2_dir + '*_s3d.fits'))
sci_x1d = sorted(glob.glob(spec2_dir + '*_x1d.fits'))

print(f"SCIENCE | Stage 2 CAL Products:\n{'-'*20}\n" + "\n".join(sci_cal))
print(f"SCIENCE | Stage 2 S3D Products:\n{'-'*20}\n" + "\n".join(sci_s3d))
print(f"SCIENCE | Stage 2 X1D Products:\n{'-'*20}\n" + "\n".join(sci_x1d))

if dospec2bg:
    # ----------------------------Background files---------------------------
    bg_cal = sorted(glob.glob(spec2_bgdir + '*_cal.fits'))
    bg_s3d = sorted(glob.glob(spec2_bgdir + '*_s3d.fits'))
    bg_x1d = sorted(glob.glob(spec2_bgdir + '*_x1d.fits'))

    print(f"BACKGROUND | Stage 2 CAL Products:\n{'-'*20}\n" + "\n".join(bg_cal))
    print(f"BACKGROUND | Stage 2 S3D Products:\n{'-'*20}\n" + "\n".join(bg_s3d))
    print(f"BACKGROUND | Stage 2 X1D Products:\n{'-'*20}\n" + "\n".join(bg_x1d))


# ---
# ## 7. Stage 3: `Spec3Pipeline` (`calwebb_spec3`)
# 
# In this section, we process our calibrated spectra from Stage 2 (`calwebb_spec2`) through the Spec3 (`calwebb_spec3`) pipeline to create Stage 3 [data products](https://jwst-pipeline.readthedocs.io/en/latest/jwst/data_products/science_products.html).
# 
# * **Input**: An ASN file that lists multiple calibrated exposures (`_cal.fits`) in addition to any background exposures (`_x1d.fits`).
# * **Output**: A single calibrated product (rectified and unrectified) and 1D spectrum. These data products have units of MJy/sr (or Jy for extracted point-source spectra).
# 	* `_cal.fits`: Calibrated 2D (unrectified) spectra (ncols x nrows).
#     * `_crf.fits`: Calibrated 2D (unrectified) spectra whose DQ array has been updated to flag pixels detected as outliers (ncols x nrows).
#     * `_s3d.fits`: Resampled 3D IFU cube (ncols x nrows x nwaves).
# 	* `_x1d.fits`: Extracted 1D spectroscopic data.
# 
# In Stage 3, single files are created for each source, one extension in the file.
# 
# The `Spec3Pipeline` performs additional corrections (e.g., outlier detection, background subtraction) and combines calibrated data from multiple exposures (e.g. a dither/nod pattern) into a single 3D spectral product, as well as a combined 1D spectrum.

# ---
# ### 7.1 Configure `Spec3Pipeline`
# 
# The `Spec3Pipeline` has the following steps available for NIRSpec IFU:
# 
# * `assign_mtwcs`: Modifies the WCS output frame in each exposure of a Moving Target (MT) observation association.
# * `master_background`: Master background subtraction.
# * `outlier_detection` : Identification of bad pixels or cosmic-rays that remain in each of the input images.
# * `pixel_replace`: Interpolates and estimates flux values for pixels flagged as DO_NOT_USE in 2D extracted spectra.
# * `cube_build`: Produces 3D spectral cubes from 2D images.
# * `extract_1d`: Extracts a 1D signal from 2D or 3D datasets.
# 
# For more information about each step and a full list of step arguments, please refer to the official documentation: [JDox](https://jwst-docs.stsci.edu/jwst-science-calibration-pipeline-overview/stages-of-jwst-data-processing/calwebb_spec3) •
# [ReadtheDocs](https://jwst-pipeline.readthedocs.io/en/latest/jwst/pipeline/calwebb_spec3.html)
# 
# Below, we set up a dictionary that defines how the `Spec3Pipeline` should be configured for IFU data.
# 
# <div class="alert alert-warning">
# If master background subtraction was chosen above, it will be applied during this stage.</br>
# To override specific steps and reference files, use the examples below. 
# </div>

# In[35]:


time_spec3 = time.perf_counter()


# In[36]:


# Set up a dictionary to define how the Spec3 pipeline should be configured.

# -------------------------Boilerplate dictionary setup-------------------------
spec3dict = {}
spec3dict['assign_mtwcs'], spec3dict['master_background'] = {}, {}
spec3dict['outlier_detection'], spec3dict['pixel_replace'] = {}, {}
spec3dict['cube_build'], spec3dict['extract_1d'] = {}, {}

# ---------------------------Override reference files---------------------------

# Overrides for various reference files.
# Files should be in the base local directory or provide full path.
#spec3dict['extract_1d']['override_extract1d'] = 'myfile.json'

# -----------------------------Set step parameters------------------------------

# Overrides for whether or not certain steps should be skipped (example).
spec3dict['outlier_detection']['skip'] = False

# Master background usage was set up above, propagate that here.
spec3dict['master_background']['skip'] = not master_bg

# Run pixel replacement code to extrapolate values for otherwise bad pixels.
# This can help mitigate 5-10% negative dips in spectra of bright sources.
# Use the 'fit_profile' algorithm.
#spec3dict['pixel_replace']['skip'] = False
#spec3dict['pixel_replace']['n_adjacent_cols'] = 5
#spec3dict['pixel_replace']['algorithm'] = 'fit_profile'

# Testing found this to be a better kernel size.
# The kernel size must only contain odd values.
spec3dict['outlier_detection']['kernel_size'] = '3 3'


# <div class="alert alert-info">
# 
# As of DMS build B9.3rc1/CAL_VER 1.11.0, a new outlier detection algorithm for IFU data has been implemented. If using a pipeline version before this build, we recommend that outlier detection be skipped/turned off. To learn more about how the algorithm operates, refer to the documentation [here](https://jwst-pipeline.readthedocs.io/en/latest/jwst/outlier_detection/outlier_detection_ifu.html#outlier-detection-ifu).
# 
# </div>

# ---
# ### 7.2 Create `Spec3Pipeline` ASN Files
# 
# [Stage 3 ASN files](https://jwst-pipeline.readthedocs.io/en/latest/jwst/associations/level3_asn_technical.html) for IFU data can include `science` and `background` exposure types. A Stage 3 ASN file requires at least one `science` file (there is usually more than one) but can contain multiple `background` files that enable master background subtraction in `calwebb_spec3`. **Note that the science exposures should be in the `_cal.fits` format, while the background exposures must be in the `_x1d.fits` format.**
# 
# This notebook downloads Stage 3 ASN files directly from MAST. However, the downloaded ASN files expect the input files to be in the same directory, which is incompatible with our directory structure. In the cell below, we update the expname fields in the ASN files to use absolute paths to ensure the pipeline looks in the correct locations.

# In[ ]:


# Get list of ALL spec3 ASN files.
spec3_asn = glob.glob(f"{asn_dir}*spec3*asn.json")
print(f"Stage 3 ASN Files:\n{'-'*20}\n" + "\n".join(spec3_asn))


# In[38]:


# Convert 'expname' paths in the ASN file to absolute paths.
# Ensures the pipeline can locate the files,
# regardless of the ASN file's location.
update_asn_paths(spec3_asn, exclude_dirs=[mast_products_dir])


# In[ ]:


# Open an ASN file as an example.
# Check that file paths have been correctly updated.
with open(spec3_asn[0], 'r') as f_obj:
    asnfile_data = json.load(f_obj)

JSON(asnfile_data, expanded=True)


# ---
# ### 7.3 Run `Spec3Pipeline`
# 
# Run the science files and, if available, any background files through the `calwebb_spec3` pipeline using the `.call()` method.

# In[ ]:


# Run Stage 3 pipeline using the custom spec3dict dictionary.

start = time.time()
if dospec3:
    for s3_asn in glob.glob(asn_dir + '*spec3*asn.json'):

        print(f"Applying Stage 3 Corrections & Calibrations to: {os.path.basename(s3_asn)}")
        spec3_result = Spec3Pipeline.call(s3_asn,
                                          save_results=True,
                                          steps=spec3dict,
                                          output_dir=spec3_dir)

    print(f"\nRun time: {round((time.time()-start)/60.0, 1)} min")
    print("Stage 3 has been completed\n")
else:
    print("Skipping Stage 3 \n")


# In[41]:


# Print output result details:
# spec3_result.__dict__  # View entire contents.
# spec3_result.meta.filename
# spec3_result.data.shape


# In[ ]:


# List the Stage 3 products.

stage3_cal = sorted(glob.glob(spec3_dir + '*_crf.fits'))
stage3_s3d = sorted(glob.glob(spec3_dir + '*_s3d.fits'))
stage3_x1d = sorted(glob.glob(spec3_dir + '*_x1d.fits'))

print(f"Stage 3 CAL Products:\n{'-'*20}\n" + "\n".join(stage3_cal))
print(f"Stage 3 S3D Products:\n{'-'*20}\n" + "\n".join(stage3_s3d))
print(f"Stage 3 X1D Products:\n{'-'*20}\n" + "\n".join(stage3_x1d))


# In[ ]:


# Print out the time benchmark
time1 = time.perf_counter()
print(f"Runtime so far: {time1 - time0:0.4f} seconds")
print(f"Runtime for Spec3: {time1 - time_spec3} seconds")


# ---
# ## 8. Visualize the data
# Define convenience funcitons for visualization.
# 
# Function to display Stage 1 products

# In[44]:


def display_rate(rates,
                 slits_models=[],
                 integration=0,
                 extname='data',
                 cmap='viridis',
                 bad_color=(1, 0.7, 0.7),
                 vmin=None,
                 vmax=None,
                 scale='asinh',
                 aspect='auto',
                 title_prefix=None,
                 title_path=False,
                 save_plot=False):
    """
    Display countrate images.

    Parameters
    ----------
    rates : list of str
        A list of RATE[INTS] files to be displayed.
    slits_models : list of str, optional
        A list of CAL[INTS] or S2D files containing the slit models.
        If provided, slit cutouts will be overlaid on the countrate images.
    integration : {None, 'min', int}, optional
        Specifies the integration to use for multi-integration data.
        If 'min', the minimum value across all integrations is used.
        If an integer, the specific integration index is used (default 0).
    extname : str, optional
        The name of the data extension to extract from ('data', 'dq', etc.).
    cmap : str, optional
        Colormap to use for displaying the image. Default is 'viridis'.
    bad_color : tuple of float, optional
        Color to use for NaN pixels. Default is light red (1, 0.7, 0.7).
    vmin : float, optional
        Minimum value for color scaling. If None, determined from the data.
    vmax : float, optional
        Maximum value for color scaling. If None, determined from the data.
    scale : {'linear', 'log', 'asinh'}, optional
        Scale to use for the image normalization. Default is 'asinh'.
    aspect : str, optional
        Aspect ratio of the plot. Default is 'auto'.
    title_prefix : str, optional
        Optional prefix for the plot title.
    title_path : bool, optional
        If True, uses the full file path for the title;
        otherwise, uses the basename. Default is False.
    save_plot : bool, optional
        If True, saves the plot as a PNG file. Default is False.
    """

    # -------------------------------Check Inputs-------------------------------
    rates = [rates] if isinstance(rates, str) else rates
    slits_models = [slits_models] if isinstance(slits_models, str) else slits_models
    nrates = len(rates)

    # ------------------------------Set up figures------------------------------
    fig, axes = plt.subplots(nrates, 1, figsize=(12, 12 * nrates),
                             sharex=True, height_ratios=[1] * nrates)
    fig.subplots_adjust(hspace=0.2, wspace=0.2)
    axes = [axes] if nrates == 1 else axes

    cmap = plt.get_cmap(cmap)  # Set up colormap and bad pixel color.
    cmap.set_bad(bad_color, 1.0)

    # ---------------------------Plot countrate image---------------------------
    for i, (rate, cal) in enumerate(itertools.zip_longest(rates,
                                                          slits_models,
                                                          fillvalue=None)):

        # -------------------Open files as JWST datamodels-------------------
        model = datamodels.open(rate)
        slits_model = datamodels.open(cal) if cal else None

        # -----------------------Extract the 2D/3D data----------------------
        data_2d = getattr(model, extname)
        if data_2d.ndim == 3:  # Handle multi-integration data.
            if integration == 'min':
                data_2d = np.nanmin(data_2d, axis=0)
            elif isinstance(integration, int) and 0 <= integration < data_2d.shape[0]:
                data_2d = data_2d[integration]
            else:
                raise ValueError(f"Invalid integration '{integration}' for 3D data.")

        # ---------------------------Scale the data-------------------------
        sigma_clipped_data = sigma_clip(data_2d, sigma=5, maxiters=3)
        vmin = np.nanmin(sigma_clipped_data) if vmin is None else vmin
        vmax = np.nanmax(sigma_clipped_data) if vmax is None else vmax
        stretch_map = {'log': LogStretch(), 'linear': LinearStretch(),
                       'asinh': AsinhStretch()}
        if scale in stretch_map:
            norm = ImageNormalize(sigma_clipped_data,
                                  interval=ManualInterval(vmin=vmin, vmax=vmax),
                                  stretch=stretch_map[scale])
        else:
            norm = simple_norm(sigma_clipped_data, vmin=vmin, vmax=vmax)

        # ----------------Plot the countrate image & colorbar---------------
        plt.subplots_adjust(left=0.05, right=0.85)
        im = axes[i].imshow(data_2d, origin='lower', cmap=cmap,
                            norm=norm, aspect=aspect, interpolation='nearest')
        units = model.meta.bunit_data
        cbar_ax = fig.add_axes([axes[i].get_position().x1 + 0.02,
                                axes[i].get_position().y0, 0.02,
                                axes[i].get_position().height])
        cbar = fig.colorbar(im, cax=cbar_ax)
        cbar.set_label(units, fontsize=12)

        # -----------------Draw slits and label source ids------------------
        # slits_model can be s2d/cal from spec2 - contains slit models for all sources.
        if slits_model:
            slit_patches = []
            for slit in slits_model.slits:
                slit_patch = Rectangle((slit.xstart, slit.ystart),
                                       slit.xsize, slit.ysize)
                slit_patches.append(slit_patch)
                y = slit.ystart + slit.ysize / 2
                x = slit.xstart if 'nrs1' in rate else slit.xstart + slit.xsize
                ha = 'right' if 'nrs1' in rate else 'left'
                plt.text(x, y, slit.source_id, color='w', ha=ha, va='center',
                         fontsize=7, path_effects=[], weight='bold')
            axes[i].add_collection(PatchCollection(slit_patches, ec='r', fc='None'))

        # -----------------Construct title and axis labels------------------
        filename = model.meta.filename
        title = (f"{title_prefix + ' ' if title_prefix else ''}"
                 f"{filename if title_path else os.path.basename(filename)}")
        if integration is not None:
            title = title.replace('rateints', f'rateints[{integration}]')
        axes[i].set_title(title, fontsize=14)
        axes[i].set_xlabel("Pixel Column", fontsize=12)
        axes[i].set_ylabel("Pixel Row", fontsize=12)

        # -------------------------Save the figure?-------------------------
        if save_plot:
            save_plot = rate.replace('fits', 'png')
            if integration:
                save_plot = save_plot.replace('.png', '%s.png' % integration)
            fig.savefig(save_plot, dpi=200)

        fig.show()


# Function to display the IFU cubes

# In[45]:


def show_ifu_cubeslices(s3d_product,
                        wavelengths,
                        spaxel_loc=[0, 0],
                        vmin=None,
                        vmax=None,
                        cmap='viridis',
                        title=None,
                        save_figure=False):

    """
    Function to that takes a 3D IFU data cube and generates:

    > 2D cube slices based on wavelength (microns).
    > Associated 1D spectrum for a designated spaxel (spatial pixel) in the data cube.
    > Corresponding 3D weight image giving the relative weights of the output spaxels.

    Parameters
    ----------
    s3d_product : list of str
        3D IFU data cube FITS file.
    wavelengths : list of float
        List of wavelength values (microns) at which to create 2D slices.
    spaxel_loc: tuple
        List of spaxel location in which to plot the associated 1D spectrum.
    cmap: str
        Color Map.
    vmin, vmax : float, float
        Minimum & Maximum signal value to use for scaling.
    title : str, optional
        Figure Title. Default is None.
    save_figure : bool, optional
        Save figure?

    Returns
    -------
    None.
    """

    # ------------------------------ Set up figure ------------------------------

    num_wavelengths = len(wavelengths) if wavelengths else 1
    fig = plt.figure(figsize=(8 * (num_wavelengths), 18))
    gs = grd.GridSpec(3, num_wavelengths, hspace=0.4, wspace=0.7,
                      height_ratios=[1]*3, width_ratios=[1]*(num_wavelengths))

    cmap_custom = cm.colors.LinearSegmentedColormap.from_list("", ["darkred",
                                                                   "darkturquoise",
                                                                   "blue"])
    colors = cmap_custom(np.linspace(0, 1, num_wavelengths))

    plot_count = 0

    # ---------------------------- Extract Cube Data ---------------------------

    root = s3d_product[:-9]  # Root file name.
    s3d = datamodels.open(s3d_product)  # 3D IFU data cube.
    x1d3 = datamodels.open(root + '_x1d.fits')  # 1D extracted spectrum.

    x1d3wave = x1d3.spec[0].spec_table.WAVELENGTH

    cube = s3d.data

    # World Coordinate System (WCS) Transformation keywords.
    wcs = WCS(fits.open(s3d_product)[1].header)
    # wcs = s3d.meta.wcs  # WCS transformation.
    wmap = s3d.weightmap  # 3D weight image.
    cdelt3 = s3d.meta.wcsinfo.cdelt3  # Axis 3 coordinate increment at reference point.
    crval3 = s3d.meta.wcsinfo.crval3  # Third axis value at the reference pixel.
    # detector = s3d.meta.instrument.detector
    grating = s3d.meta.instrument.grating
    ffilter = s3d.meta.instrument.filter
    # bunit = s3d.meta.bunit_data

    # Wavelength range of the grating/filter combination.
    wavstart = s3d.meta.wcsinfo.waverange_start
    wavend = s3d.meta.wcsinfo.waverange_end

    # Loop through each wavelength slices.
    for i, wslice in enumerate(wavelengths):

        if float(wavstart) <= wslice*10**-6 <= float(wavend):

            # ------------------------- Plot wavelength slice -------------------------
            nslice = int((wslice - crval3)/cdelt3)  # The slice of the cube.
            slice_mean = np.nanmean(cube[(nslice-2):(nslice+2), :, :], axis=0)
            if not vmin and not vmax:
                vmin = np.nanpercentile(slice_mean, 2)
                vmax = np.nanpercentile(slice_mean, 98)
            slice_norm = ImageNormalize(slice_mean, vmin=vmin,
                                        vmax=vmax, stretch=AsinhStretch())
            ax1 = plt.subplot(gs[plot_count], projection=wcs, slices=('x', 'y', nslice))
            slice_image = ax1.imshow(slice_mean, norm=slice_norm,
                                     origin='lower', aspect='auto', cmap=cmap)
            cb_image = fig.colorbar(slice_image, fraction=0.046, pad=0.04)
            cb_image.set_label('MJy/sr', labelpad=-1, fontsize=22)
            cb_image.ax.tick_params(labelsize=20)
            cb_image.ax.yaxis.get_offset_text().set_fontsize(20)

            ax1.set_xlabel('RA', fontsize=22)
            ax1.set_ylabel('DEC', labelpad=-1, fontsize=22)
            ax1.set_title(
                f"{os.path.basename(s3d_product)}\n"
                f"Grating/Filter: {grating}/{ffilter}\n"
                f"{wslice} microns",
                fontsize=20)
            ax1.tick_params(axis='both', which='major', labelsize=15)
            ax1.coords[0].set_ticklabel(rotation=13, ha='right', pad=24)

            # ------------------------- Plot spaxel spectrum -------------------------
            # Zoom in on a Spaxel: Spectrum
            x1d3flux_loc = cube[:, spaxel_loc[1], spaxel_loc[0]]
            ax2 = plt.subplot(gs[num_wavelengths + plot_count])

            ax2.plot(x1d3wave, x1d3flux_loc, linewidth=1, color=colors[i])
            spaxel_rect = plt.Rectangle((spaxel_loc[0]-.5, spaxel_loc[1]-.5), 1, 1,
                                        fill=False, color='black', linewidth=2)
            ax1.add_patch(spaxel_rect)

            ax2.grid(linewidth=2)
            ax2.set_xlabel('$\u03BB [\u03BC$m]', fontsize=22)
            ax2.set_ylabel("Surface Brightness \n (MJy/sr)", fontsize=22)
            ax2.set_title('Spaxel at (x, y)=' + repr(spaxel_loc), fontsize=25)
            ax2.tick_params(axis='both', which='major', labelsize=15)
            ax2.yaxis.get_offset_text().set_fontsize(15)

            # ------------------------- Plot weight slice -------------------------
            # Corresponding Weight Map (wmap) for cube slice.
            ax3 = plt.subplot(gs[2*num_wavelengths + plot_count],
                              projection=wcs, slices=('x', 'y', nslice))
            slice_mean_wmap = np.nanmean(wmap[(nslice-2):(nslice+2), :, :], axis=0)
            slice_norm_wmap = ImageNormalize(slice_mean_wmap, stretch=AsinhStretch())
            slice_wmap = ax3.imshow(slice_mean_wmap, norm=slice_norm_wmap,
                                    origin='lower', aspect='auto', cmap=cmap)
            cb_wmap = fig.colorbar(slice_wmap, fraction=0.046, pad=0.04)
            cb_wmap.set_label('Weight', labelpad=-1, fontsize=22)
            cb_wmap.ax.tick_params(labelsize=20)
            cb_wmap.ax.yaxis.get_offset_text().set_fontsize(20)

            ax3.set_xlabel('RA', fontsize=22)
            ax3.set_ylabel('DEC', labelpad=-1, fontsize=22)
            ax3.set_title(str(wslice)+' microns: Weight Map', fontsize=25)
            ax3.tick_params(axis='both', which='major', labelsize=15)
            ax3.coords[0].set_ticklabel(rotation=13, ha='right', pad=24)
            # Scale information.
            ax2.set_ylim(np.nanpercentile(x1d3flux_loc, 2),
                         np.nanpercentile(x1d3flux_loc, 98))
            ax2.xaxis.set_tick_params(labelsize=20)
            ax2.yaxis.set_tick_params(labelsize=20)
            ax2.set_aspect(0.5/ax2.get_data_ratio())
            plot_count += 1

    if title:
        fig.suptitle(title, fontsize=25)
        plt.subplots_adjust(top=0.8)

    fig.tight_layout(rect=[0, 0, 0.98, 0.98])

    if save_figure:
        fig.savefig(root+".png", dpi=24, bbox_inches="tight")


# ### 8.1 Display `Detector1Pipeline` Products
# Inspect the Stage 1 slope products. If `compare_mast` is enabled, an additional plot will compare the reprocessed results with MAST products, which were processed using the default pipeline parameters. Reprocessing with a newer pipeline version may also result in noticeable improvements in data quality.

# In[ ]:


rate_file = rate_sci[-1]  # Show the last rate file, as an example.

display_rate(rate_file, vmin=0, vmax=2, scale='asinh',
             aspect=1, title_prefix='REPROCESSED')  # , extname='dq')


# ---
# ### 8.2 Display `Spec2Pipeline` Products
# 
# Inspect the Stage 2 calibrated spectra. 

# In[ ]:


# 8.2 Display Spec2Pipeline Products
cube = sci_s3d[-2]  # Show one cube file, as an example.
x1d_file = sci_x1d[-2]

# Slices may be blank if the spectrum falls on the other detector at that wavelength.
wavelengths = [3.0, 3.4, 4.0]  # Wavelength slices (um) to take from the 3D data cube.
spaxel_loc = [30, 29]  # Spaxel locations for associated 1D spectrum [x, y].

# Define parameters for the plot.
title = 'Level 2 IFU Product: 3D Cube Slices vs. Corresponding 3D Weighted Map'

show_ifu_cubeslices(cube, wavelengths=wavelengths,
                    spaxel_loc=spaxel_loc, title='REPROCESSED '+title)


# ### 8.3 Display `Spec3Pipeline` Products
# Inspect the Stage 3 combined calibrated spectra. 

# In[ ]:


fig = plt.figure(figsize=(15, 9))

x1d = datamodels.open(x1d_file)
x1d_wave = x1d.spec[0].spec_table.WAVELENGTH
x1d_flux = x1d.spec[0].spec_table.SURF_BRIGHT
grating = x1d.meta.instrument.grating
ffilter = x1d.meta.instrument.filter
plt.plot(x1d_wave, x1d_flux, linewidth=2, label=f'REPROCESSED ({grating}/{ffilter})')

for wave in wavelengths:
    plt.vlines(wave, np.nanpercentile(x1d_flux, 2), np.nanpercentile(x1d_flux, 98),
               'black', 'dotted', label=f'{wave} microns', linewidth=5)
plt.xlabel('Wavelength (μm)', fontsize=15)
plt.ylabel('Surface Brightness (MJy/sr)', fontsize=15)
plt.title("Level 2 IFU Product: Extracted 1D Spectrum",
          fontsize=20)
plt.ylim(np.nanpercentile(x1d_flux, 2), np.nanpercentile(x1d_flux, 98))
plt.legend()


# In[ ]:


cube = stage3_s3d[0]  # Show the last cube file, as an example.
x1d_file = stage3_x1d[0]

# Define parameters for the plot.
title = 'Level 3 IFU Product: 3D Cube Slices vs. Corresponding 3D Weighted Map'

# Slices may be blank if the spectrum falls on the other detector at that wavelength.
wavelengths = [3.0, 3.4, 4.0]  # Wavelength slices (um) to take from the 3D data cube.
spaxel_loc = [30, 29]  # Spaxel locations for associated 1D spectrum [x, y].

show_ifu_cubeslices(cube, wavelengths=wavelengths,
                    spaxel_loc=spaxel_loc, title='REPROCESSED '+title)


# In[ ]:


fig = plt.figure(figsize=(15, 9))

x1d = datamodels.open(x1d_file)
x1d_wave = x1d.spec[0].spec_table.WAVELENGTH
x1d_flux = x1d.spec[0].spec_table.SURF_BRIGHT
grating = x1d.meta.instrument.grating
ffilter = x1d.meta.instrument.filter

plt.plot(x1d_wave, x1d_flux, linewidth=2, label=f'REPROCESSED ({grating}/{ffilter})')

for wave in wavelengths:
    plt.vlines(wave, np.nanpercentile(x1d_flux, 2), np.nanpercentile(x1d_flux, 98),
               'black', 'dotted', label=f'{wave} microns', linewidth=5)
plt.xlabel('Wavelength (μm)', fontsize=15)
plt.ylabel('Surface Brightness (MJy/sr)', fontsize=15)
plt.title("Level 2 IFU Product: Extracted 1D Spectrum",
          fontsize=20)
plt.ylim(np.nanpercentile(x1d_flux, 2), np.nanpercentile(x1d_flux, 98))
plt.legend()


# ---
# 
# ## 9. Modifying the EXTRACT1D Reference File (as needed)
# 
# The `extract_1d` step is controlled by a different set of parameters in the EXTRACT1D reference file for extended vs. point source IFU data. 
# 
# [Extraction for 3D IFU Data:](https://jwst-pipeline.readthedocs.io/en/latest/jwst/extract_1d/description.html)
# 
# > * For extended sources, rectangular aperture photometry is used, with the entire image extracted and no background subtraction, regardless of what is specified in the reference file or step arguments.
# > * For point source data, the extraction aperture is centered at the RA/DEC target location indicated by the header. If the target location is undefined in the header, then the extraction region is the center of the IFU cube.
# > * For point sources, a circular extraction aperture is used, along with an optional circular annulus for background extraction and subtraction. The size of the extraction region and the background annulus size varies with wavelength. The extraction-related vectors are found in the ASDF EXTRACT1D reference file. For each element in the wavelength vector, there are three size components: `radius`, `inner_bkg`, and `outer_bkg`. The radius vector sets the extraction size while `inner_bkg` and `outer_bkg` specify the limits of an annular background aperture. 
# 
# Below is an example of how to modify the EXTRACT1D reference file for point sources. More information about this file and how to modify it in [extract_1d](https://jwst-pipeline.readthedocs.io/en/latest/jwst/extract_1d) and
# [Editing JSON reference file](https://jwst-pipeline.readthedocs.io/en/latest/jwst/extract_1d/reference_files.html#editing-json-reference-file-format-for-non-ifu-data).
# 
# <div class="alert alert-block alert-info">
# 
# The `ifu_autocen` parameter provides a new method to center on the point sources even if the header information is imperfect due to inaccuracies caused by, e.g., FGS.
# 
# </div>
# 
# <div class="alert alert-block alert-danger">
#     
# **Warning**: Currently, there is no aperture correction in place for NIRSpec, so the `radius` parameter **MUST** remain unchanged for point source to ensure proper flux calibration!
# 
# </div>

# In[ ]:


# If you don't know the reference file name this should work.
# extract_1d_ref = Spec3Pipeline().get_reference_file(stage3_s3d, 'extract1d')

refs = api.dump_references(crds_client.get_context_used('jwst'),
                           ['jwst_nirspec_extract1d_0002.asdf'])
extract_1d_ref = refs['jwst_nirspec_extract1d_0002.asdf']

# Construct the modified file name
basename = os.path.basename(extract_1d_ref)[:-5]  # Remove ".asdf"
extract_1d_ref_mod = os.path.join(os.environ['CRDS_PATH'], f"{basename}_ifu.asdf")

print(basename, extract_1d_ref_mod)

# Open the original ASDF file, modify it, and save the modified version.
with asdf.open(extract_1d_ref, mode='r') as ref_file:
    # Create a copy of the original tree
    tree = ref_file.tree.copy()

    # Modify the tree
    tree['data']['radius'] = np.full((2048,), 0.45, dtype='float32')
    tree['data']['inner_bkg'] = np.full((2048,), 1.0, dtype='float32')
    tree['data']['outer_bkg'] = np.full((2048,), 1.2, dtype='float32')

    # Save the modified tree to a new file
    with asdf.AsdfFile(tree) as new_file:
        new_file.write_to(extract_1d_ref_mod)


# In[ ]:


# Check modified file contents
with asdf.open(extract_1d_ref_mod) as ref_file:
    # Pretty-print the ASDF tree structure
    pprint(ref_file.tree, depth=4)


# Now, we re-extract the 1D spectrum by running the `Extract1dStep` and overriding the reference file.

# In[ ]:


for s3d in stage3_s3d:
    Extract1dStep.call(stage3_s3d,
                       save_results=True,
                       output_dir=spec3_dir,
                       output_use_model=True,
                       suffix='x1d_mod',  # Default suffix is `_extract1dstep.fits`
                       use_source_posn=False,
                       ifu_autocen=False,
                       override_extract1d=extract_1d_ref_mod)


# We now plot again the 3D/1D final cube/spectra and showing the original extraction box in red and the new extraction box in black.

# In[ ]:


# Load necessary files
stage3_x1d_mod = sorted(glob.glob(spec3_dir + '*_x1d_mod.fits'))
x1d_file = stage3_x1d_mod[0]
cube_data = datamodels.open(cube).data
x1d_mod = datamodels.open(x1d_file)
x1d_wave_mod = x1d_mod.spec[0].spec_table.WAVELENGTH
x1d_flux_mod = x1d_mod.spec[0].spec_table.SURF_BRIGHT

# Setup the figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(25, 9),
                               gridspec_kw={'width_ratios': [5, 3],
                                            'wspace': 0.1})

# Plot the original and modified spectra
ax1.plot(x1d_wave, x1d_flux, linewidth=2, label="Original Extraction")
ax1.plot(x1d_wave_mod, x1d_flux_mod, linewidth=2, label="Modified Extraction")
ax1.set_xlabel('Wavelength (μm)', fontsize=15)
ax1.set_ylabel('Flux (Jy)', fontsize=15)
ax1.set_title("Level 3 IFU Product: Extracted 1D Spectrum", fontsize=20)
ax1.set_ylim(np.nanpercentile(x1d_flux, 2), np.nanpercentile(x1d_flux, 98))
ax1.ticklabel_format(axis='y', style='sci', scilimits=(0, -2))
ax1.legend(fontsize=15)

# Plot the IFU cube slice
slice_mean = np.nanmean(cube_data[400:500, :, :], axis=0)
slice_full = ax2.imshow(slice_mean,
                        norm=ImageNormalize(vmin=0, vmax=150, stretch=AsinhStretch()),
                        origin='lower', cmap='viridis')
plt.colorbar(slice_full, ax=ax2,
             fraction=0.046, pad=0.04).set_label('MJy/sr', fontsize=15)

# Annotate the extraction regions
with asdf.open(extract_1d_ref_mod, mode='r') as ref_file:
    radii_data = ref_file.tree['data']
    print("Radius [arcsec]:", radii_data['radius'][0])
    print("Inner background [arcsec]:", radii_data['inner_bkg'][0])
    print("Outer background [arcsec]:", radii_data['outer_bkg'][0])

    if x1d_mod.spec[0].source_type == 'POINT':
        x_cen, y_cen = x1d_mod.spec[0].extraction_x, x1d_mod.spec[0].extraction_y
        for label, radius, color in zip(['Radius', 'Inner Background Radius',
                                         'Outer Background Radius'],
                                        ['radius', 'inner_bkg', 'outer_bkg'],
                                        ['black', 'blue', 'red']):
            ax2.add_patch(Circle((x_cen, y_cen), radii_data[radius][0] * 10,
                                 fill=False, color=color, label=label))

    ax2.set_xlabel('X (pixels)', fontsize=15)
    ax2.set_ylabel('Y (pixels)', fontsize=15)
    ax2.set_title("Full IFU Cube: \n Extraction Region Preview", fontsize=20)
    ax2.legend(fontsize=15)

plt.show()


# **The spectra will look identical if the source is extended.**

# ---
# ## Related Notebooks
# 
# 
# * [NIRSpec Workaround Notebooks](https://github.com/spacetelescope/jwst-caveat-examples/tree/main/NIRSPEC_General)
# * [JDAT: JWST Data Analysis Example Notebooks](https://github.com/spacetelescope/jdat_notebooks/tree/main/notebooks)
# 
# ---

# <figure>
#        <img src="https://raw.githubusercontent.com/spacetelescope/notebooks/master/assets/stsci_pri_combo_mark_horizonal_white_bkgd.png" alt="Space Telescope Logo\" align="right" style="width: 200px"/>
# </figure>
#    
# [Top of Page](#NIRSpec-IFU-Pipeline-Notebook)
