import os
from astroquery.mast import Mast
import numpy as np
import astropy
import astropy.table
from astropy.time import Time
import requests

def set_params(parameters):
    """
    Utility function for making dicts used in MAST queries.

    """
    return [{'paramName': p, 'values': v if isinstance(v, list) else [v]} for p, v in parameters.items()]

def query_coron_datasets(inst,
                         filt=None,
                         mask=None,
                         kind=None,
                         subarray=None,
                         program=None,
                         obsnum=None,
                         channel=None,
                         ignore_cal=True,
                         ignore_ta=True,
                         verbose=False,
                         level=None,
                         ignore_exclusive_access=False,
                         exp_type=None,
                         return_filenames=False):
    """
    Query MAST to make a summary table of existing JWST coronagraphic datasets.

    Parameters
    ----------
    inst : str
        'NIRCam' or 'MIRI'. Required.
    filt : str
        Filter name, like 'F356W'. Required.
    mask : str
        Coronagraph mask name, like 'MASKA335R' or '4QPM_1550'. Optional.
        If provided, must exactly match the keyword value as used in MAST,
        which isn't always what you might expect. In particular, you need to
        explicitly include the "A" for the NIRCam A module in e.g.,
        'MASKA335R'.
    kind : str
        'SCI' for science targets, 'REF' for PSF references, or 'BKG' for
        backgrounds.
    channel : str
        For NIRCam only, channel name, "SW" or "SHORT" versus "LW" or "LONG".
        Leave blank for both.
    ignore_ta : bool
        Ignore/exclude any target acquisition exposures. This can be
        useful to only include science and reference images.
    ignore_cal : bool
        Ignore/exclude any category='CAL' calibration programs. This can be
        desirable to ignore the NIRCam coronagraphic flux calibration data
        sets, which otherwise look like science data to this query (programs
        1537 and 1538 for example).
    exp_type : list of strings, or None
        By default, the value for the MAST query field on exposure type is
        determined automatically, based on whether or not ignore_ta is set.
        Set this optional parameter if you want to control the exp_type value
        used in the query directly.
    ignore_exclusive_access : bool
        Whether or not to ignore (filter out from query results) any data which
        is still under exclusive access restrictions to the original proposing team.
        For example, query for kind='REF', ignore_exclusive_access=True to find
        only the publicly-available PSF references that can be downloaded by anyone.
    return_filenames : bool
        Return a shorter summary table of observations, versus returning a
        more comprehensive longer table of individual exposures and filenames?
    level : str
        Desired JWST data product level for filenames.
        '1b' or 'uncal', '2a' or 'rate', etc.
        For historical reasons it's not possible to easily query MAST directly for
        products earlier than level 2b (cal/calints); MAST "hides" lower level files
        once higher level products are available. Thus this works by querying for the
        level 2b products, and performing filename transformation on them

    Returns
    -------
    None.

    """

    # Perform MAST query to find all available datasets for a given
    # filter/occulter.
    if inst.upper() == 'MIRI':
        service = 'Mast.Jwst.Filtered.Miri'
        template = 'MIRI Coronagraphic Imaging'
    else:
        service = 'Mast.Jwst.Filtered.NIRCam'
        template = 'NIRCam Coronagraphic Imaging'

    keywords = {
        'template': [template],
        'productLevel': ['2b'],
    }
    if filt is not None:
        keywords['filter'] = [filt,]
    if obsnum is not None:
        keywords['observtn'] = obsnum if isinstance(obsnum, list) else [obsnum,]
        keywords['observtn'] = [str(a) for a in keywords['observtn']] # must be string type!

    if mask is not None:
        keywords['coronmsk'] = [mask]
    if ignore_cal:
        keywords['category'] = ['ERS', 'GTO', 'GO', 'DD',]  # but not CAL
    if ignore_ta:
        keywords['exp_type'] = ['NRC_CORON', 'MIR_LYOT', 'MIR_4QPM']  # but not NRC_TACQ or MIRI_TACQ or NRC_TACONFIRM
    if exp_type:
        # Optional, allow user to custom override exp_type, for instance to query specifically for TA_CONFIRM exposures
        keywords['exp_type'] = exp_type

    # Optional, restrict to one apt program
    if program is not None:
        keywords['program'] = [f'{program:05d}',]

    # Optional, restrict to one kind of coronagraphic data
    if kind is not None:
        if kind.upper() == 'SCI':
            keywords['is_psf'] = ['f']
            keywords['bkgdtarg'] = ['f']
        elif kind.upper() == 'REF':
            keywords['is_psf'] = ['t']
            keywords['bkgdtarg'] = ['f']
        elif kind.upper() == 'BKG':
            keywords['is_psf'] = ['f']
            keywords['bkgdtarg'] = ['t']

    if inst.upper()=='NIRCAM' and channel is not None:
        if channel.upper().startswith('S'):
            keywords['channel'] = ['SHORT',]
        elif channel.upper().startswith('L'):
            keywords['channel'] = ['LONG', ]
        else:
            raise RuntimeError("Invalid channel")

    if subarray is not None:
        keywords['subarray'] = [subarray,]

    # Method note: we query MAST for much more than we actually need/want, and
    # then filter down afterward. This is not entirely necessary, but leaves
    # room for future expansion to add options for more verbose output, etc.
    # Currently, this works by retrieving all level2b (i.e., cal/calints)
    # files, including all dithers etc., and then trimming to one unique row
    # per observation.
    collist = (
        'filename, productLevel, filter, coronmsk, targname, duration, '
        'effexptm, effinttm, exp_type, bkgdtarg, bstrtime, is_psf, nexposur, '
        'nframes, nints, numdthpt, obs_id, observtn, obslabel, pi_name, program, '
        'subarray, template, title, visit_id, visitsta, vststart_mjd, '
        'isRestricted, publicReleaseDate_mjd'
    )
    all_columns = False

    parameters = {'columns': '*' if all_columns else collist,
                  'filters': set_params(keywords)}
    if verbose:
        print("MAST query parameters:")
        print(parameters)

    responsetable = Mast.service_request(service, parameters)
    responsetable.sort(keys='bstrtime')

    # Add the initial V to visit ID.
    responsetable['visit_id'] = astropy.table.Column(responsetable['visit_id'], dtype=np.dtype('<U12'))
    for row in responsetable:
        row['visit_id'] = 'V' + row['visit_id']

    # Add a summary for which kind of observation each is.
    kind = np.zeros(len(responsetable), dtype='a3')
    kind[:] = 'SCI'  # by default assume SCI, then check for REF and BKG and TA
    kind[responsetable.columns['is_psf'] == 't'] = 'REF'
    kind[responsetable.columns['bkgdtarg'] == 't'] = 'BKG'
    for ta_type in ['NRC_TACQ', 'NRC_TACONFIRM', 'MIRI_TACQ']:
        kind[responsetable.columns['exp_type'] == ta_type] = 'TA'
    kind[kind == ''] = 'SCI'
    responsetable.add_column(astropy.table.Column(kind), index=2, name='kind')

    if ignore_exclusive_access:
        mjd_now = astropy.time.Time.now().mjd
        public_data = responsetable['publicReleaseDate_mjd'] < mjd_now
        responsetable = responsetable[public_data]

    if return_filenames:

        if level is not None and level.lower() != 'cal' and level.lower() != '2b':
            # Transform filenames to either rate or uncal files
            # This may not be robust to all possible scenarios yet...
            if level.lower()=='rate' or level.lower()=='2a':
                responsetable['filename'] = [f.replace('_cal', '_rate') for f in responsetable['filename']]
                responsetable['productLevel'] = '2a'
            elif level.lower() == 'uncal' or level.lower() == '1b':
                responsetable['filename'] = [f.replace('_calints', '_uncal').replace('_cal', '_uncal') for f in responsetable['filename']]
                responsetable['productLevel'] = '1b'

        return responsetable

    # Summarize the distinct observations conveniently.
    cols_to_keep = ['visit_id', 'filter', 'coronmsk', 'targname', 'obslabel',
                    'duration', 'numdthpt', 'program', 'title', 'pi_name']

    summarytable = astropy.table.Table([responsetable.columns[cname].filled() for cname in cols_to_keep],
                                       masked=False,
                                       copy=True)

    summarytable.add_column(astropy.table.Column(astropy.time.Time(responsetable['vststart_mjd'], format='mjd').iso, dtype=np.dtype('<U16')),
                            index=1,
                            name='start time')

    summarytable = astropy.table.unique(summarytable)
    summarytable.sort(keys='start time')

    return summarytable

def get_mast_filename(filename, outputdir='.',
                      overwrite=False, exists_ok=True, verbose=True,
                      mast_api_token=None):
    """Download any specified filename from MAST, writing to outputdir

    If a file exists already, default is to not download.
    Set overwrite=True to overwrite existing output file.
    or set exists_ok=False to raise ValueError.

    verbose toggles on/off minor informative text output

    Other parameters are less likely to be useful:
    Default mast_api_token comes from MAST_API_TOKEN environment variable.

    Adapted from example code originally by Rick White, STScI, via archive help desk.
    """

    # if not mast_api_token:
    #     mast_api_token = os.environ.get('MAST_API_TOKEN')
    #     if mast_api_token is None:
    #         raise ValueError("Must define MAST_API_TOKEN env variable or specify mast_api_token parameter")
    assert '/' not in filename, "Filename cannot include directories"

    mast_url = "https://mast.stsci.edu/api/v0.1/Download/file"

    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    elif not os.path.isdir(outputdir):
        raise ValueError(f"Output location {outputdir} is not a directory")
    elif not os.access(outputdir, os.W_OK):
        raise ValueError(f"Output directory {outputdir} is not writable")
    outfile = os.path.join(outputdir, filename)

    if (not overwrite) and os.path.exists(outfile):
        if exists_ok:
            if verbose:
                print(" ALREADY DOWNLOADED: "+outfile)
            return
        else:
            raise ValueError(f"{outfile} exists, not overwritten")

    mast_api_token = None
    r = requests.get(mast_url, params=dict(uri=f"mast:JWST/product/{filename}"),
                     headers=dict(Authorization=f"token {mast_api_token}"), stream=True)
    r.raise_for_status()

    block_size = 1024000
    with open(outfile, 'wb') as fd:
        for data in r.iter_content(chunk_size=block_size):
            fd.write(data)

    if verbose:
        print(" DOWNLOAD SUCCESSFUL: "+outfile)


def download_files(product_table, outputdir='.', verbose=True, **kwargs):
    """Retrieve data products from MAST

    Parameters
    ----------
    product_table : astropy.table
        Table of MAST products, as returned by astroquery.Mast
    outputdir : str
        Directory where to save the output products
    verbose : bool
        Toggle text information output

    Other kwargs are passed to get_mast_filename

    """

    # depending on which mast service is used, the filename column is inconsistently labeled
    # in particular the Observations search vs. keyword search interfaces.
    # in returned products
    if 'filename' in product_table.colnames:
        fn_key = 'filename'
    elif 'productFilename' in product_table.colnames:
        fn_key = 'productFilename'
    else:
        raise RuntimeError("Cannot find filename column in that table")

    product_table.sort(keys=fn_key)

    for row in product_table:
        if verbose:
            if 'size' in row.colnames:
                print(f"{row[fn_key]} : {row['size']/(1024**2):.2f} MB")
        get_mast_filename(row[fn_key], outputdir=outputdir, verbose=verbose,
                          **kwargs)


def get_obs_info(file):
    """
    Given a JWST filename, return a dict of observation info:
    inst, filt, mask, visit start
    """

    from jwst import datamodels

    with datamodels.open(file) as dm:
        inst = dm.meta.instrument.name
        filt = dm.meta.instrument.filter
        mask = dm.meta.instrument.coronagraph
        visit_start = Time(dm.meta.visit.start_time).mjd

    return {'inst': inst,
            'filt': filt,
            'mask': mask,
            'vstart': visit_start}

def download_coron_references(files,
                          num_refs=2,
                          download_dir='./REFS/',
                          kind='REF',
                          subarray=None,
                          program=None,
                          obsnum=None,
                          channel=None,
                          ignore_cal=True,
                          ignore_ta=True,
                          verbose=False,
                          level='2b',
                          ignore_exclusive_access=False,
                          exp_type=None,
                          return_filenames=True):
    """
    Convenience wrapper around query_coron_datasets to find the closest N coronagraphic
    PSF reference datasets for one or more science files.

    Parameters
    ----------
    files : str or list
        A single science filename or a list of science filenames. The first
        file is used to determine instrument/filter/mask for the MAST query.
        Any rows in the MAST result whose basename matches any of the provided
        filenames will be removed from consideration.
    num_refs : int
        Number of reference datasets to return, sorted by closest in time to the input file. Default is 2.

    See query_coron_datasets for additional parameter details.
    """

    # Accept either a single filename or a list
    if isinstance(files, (list, tuple, np.ndarray)):
        files_list = list(files)
        if len(files_list) == 0:
            raise ValueError("`files` list is empty")
    else:
        files_list = [files]

    # Use the first file to get observation info (instrument/filter/mask)
    obs_info = get_obs_info(files_list[0])

    # Query MAST for suitable reference datasets
    db = query_coron_datasets(inst=obs_info['inst'],
                              filt=obs_info['filt'],
                              mask=obs_info['mask'],
                              kind=kind,
                              subarray=subarray,
                              program=program,
                              obsnum=obsnum,
                              channel=channel,
                              ignore_cal=ignore_cal,
                              ignore_ta=ignore_ta,
                              verbose=verbose,
                              level=level,
                              ignore_exclusive_access=ignore_exclusive_access,
                              exp_type=exp_type,
                              return_filenames=return_filenames)

    # If the query returned filenames and the user provided science files, remove
    # any rows that match those science filenames (compare basenames).
    if return_filenames and db is not None and len(db) > 0:
        # Determine which column holds filenames
        if 'filename' in db.colnames:
            fn_col = 'filename'
        elif 'productFilename' in db.colnames:
            fn_col = 'productFilename'
        else:
            fn_col = None

        if fn_col is not None:
            # Build a set of basenames to exclude
            science_basenames = {os.path.basename(str(f)) for f in files_list}

            # Extract basenames from db rows safely
            db_basenames = [os.path.basename(str(x)) for x in db[fn_col]]

            # Create a boolean mask of rows to keep (those not matching any science basename)
            keep_mask = [bn not in science_basenames for bn in db_basenames]

            # Apply mask to db
            try:
                db = db[keep_mask]
                if verbose:
                    print(f"Filtered out {np.count_nonzero(~np.array(keep_mask))} rows matching provided science files from MAST results")
            except Exception:
                # Fallback: if boolean indexing fails, build a new table
                rows = [row for keep, row in zip(keep_mask, db) if keep]
                db = astropy.table.Table(rows, names=db.colnames)

    # If MIRI, need to exclude observations from program 1193 and 1386, as they don't have glowstick subtraction
    if obs_info['inst'].upper() == 'MIRI':
        if verbose:
            print(f"Excluding MIRI observations from programs 1193 and 1386, as they don't have glowstick subtraction")
        if 'program' in db.colnames:
            db = db[~np.isin(db['program'], [1193, 1386])]
        else:
            if verbose:
                print("Warning: 'program' column not found in MAST results; cannot filter out MIRI programs 1193 and 1386")

    # If after filtering there are no rows left, warn and return
    if db is None or len(db) == 0:
        if verbose:
            print("No reference candidates found after filtering; nothing to download.")
        return

    # Now filter to get only the "num_refs" closest references in time. Can use the visit start
    # Get the unique values of vststart_mjd in the db
    ref_visit_starts = np.unique(db['vststart_mjd'])

    # Find closest num_refs visit starts to the science observation visit start
    time_diffs = np.abs(ref_visit_starts - obs_info['vstart'])
    closest_indices = np.argsort(time_diffs)[:num_refs]
    closest_visit_starts = ref_visit_starts[closest_indices]

    # Now get all rows in db that match these closest visit starts
    mask = np.isin(db['vststart_mjd'], closest_visit_starts)
    closest_dbs = db[mask]

    download_files(closest_dbs, outputdir=download_dir, verbose=verbose)
