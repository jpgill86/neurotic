# -*- coding: utf-8 -*-
"""
The :mod:`neurotic.datasets.metadata` module implements a class for reading
metadata files.

.. autoclass:: MetadataSelector
   :members:
"""

import os
import urllib
import yaml

from ..datasets.download import download

import logging
logger = logging.getLogger(__name__)


class MetadataSelector():
    """
    A class for managing metadata.

    A metadata file can be specified at initialization, in which case it is
    read immediately. The file contents are stored as a dictionary in
    :attr:`all_metadata`.

    >>> metadata = MetadataSelector(file='metadata.yml')
    >>> print(metadata.all_metadata)

    File contents can be reloaded after they have been changed, or after
    changing ``file``, using the :meth:`load` method.

    >>> metadata = MetadataSelector()
    >>> metadata.file = 'metadata.yml'
    >>> metadata.load()

    A particular metadata set contained within the file can be selected at
    initialization with ``initial_selection`` or later using the :meth:`select`
    method. After making a selection, the selected metadata set is accessible
    at :meth:`metadata.selected_metadata <selected_metadata>`, e.g.

    >>> metadata = MetadataSelector(file='metadata.yml')
    >>> metadata.select('Data Set 5')
    >>> print(metadata.selected_metadata['data_file'])

    A compact indexing method is implemented that allows the selected metadata
    set to be accessed directly, e.g.

    >>> print(metadata['data_file'])

    This allows the MetadataSelector to be passed to functions expecting a
    simple dictionary corresponding to a single metadata set, and the selected
    metadata set will be used automatically.

    Files associated with the selected metadata set can be downloaded
    individually or all together, e.g.

    >>> metadata.download('video_file')

    or

    >>> metadata.download_all_data_files()

    The absolute path to a local file or the full URL to a remote file
    associated with the selected metadata set can be resolved with the
    :meth:`abs_path` and :meth:`abs_url` methods, e.g.

    >>> print(metadata.abs_path('data_file'))
    >>> print(metadata.abs_url('data_file'))
    """

    def __init__(self, file=None, local_data_root=None, remote_data_root=None, initial_selection=None):
        """
        Initialize a new MetadataSelector.
        """

        self.file = file
        self.local_data_root = local_data_root
        self.remote_data_root = remote_data_root

        self.all_metadata = None  #: A dictionary containing the entire file contents, set by :meth:`load`.
        self._selection = None
        if self.file is not None:
            self.load()
            if initial_selection is not None:
                self.select(initial_selection)

    def load(self):
        """
        Read the metadata file.
        """
        self.all_metadata = _load_metadata(self.file, self.local_data_root, self.remote_data_root)
        if self._selection not in self.all_metadata:
            self._selection = None

    def select(self, selection):
        """
        Select a metadata set.
        """
        if self.all_metadata is None:
            logger.critical('Load metadata before selecting')
        elif selection not in self.all_metadata:
            raise ValueError('{} was not found in {}'.format(selection, self.file))
        else:
            self._selection = selection

    @property
    def selected_metadata(self):
        """
        The access point for the selected metadata set.
        """
        if self._selection is None:
            return None
        else:
            return self.all_metadata[self._selection]

    def abs_path(self, file):
        """
        Convert the relative path of ``file`` to an absolute path using
        ``data_dir``.
        """
        return _abs_path(self.selected_metadata, file)

    def abs_url(self, file):
        """
        Convert the relative path of ``file`` to a full URL using
        ``remote_data_dir``.
        """
        return _abs_url(self.selected_metadata, file)

    def download(self, file, **kwargs):
        """
        Download a file associated with the selected metadata set.

        See :func:`neurotic.datasets.download.download` for possible keyword
        arguments.
        """
        _download_file(self.selected_metadata, file, **kwargs)

    def download_all_data_files(self, **kwargs):
        """
        Download all files associated with the selected metadata set.

        See :func:`neurotic.datasets.download.download` for possible keyword
        arguments.
        """
        _download_all_data_files(self.selected_metadata, **kwargs)

    def __iter__(self, *args):
        return self.selected_metadata.__iter__(*args)

    def __getitem__(self, *args):
        return self.selected_metadata.__getitem__(*args)

    def __setitem__(self, *args):
        return self.selected_metadata.__setitem__(*args)

    def __delitem__(self, *args):
        return self.selected_metadata.__delitem__(*args)

    def get(self, *args):
        return self.selected_metadata.get(*args)

    def setdefault(self, *args):
        return self.selected_metadata.setdefault(*args)


def _load_metadata(file = 'metadata.yml', local_data_root = None, remote_data_root = None):
    """
    Read metadata stored in a YAML file about available collections of data,
    assign defaults to missing parameters, and resolve absolute paths for local
    data stores and full URLs for remote data stores.

    ``local_data_root`` must be an absolute or relative path on the local
    system, or None. If it is a relative path, it is relative to the current
    working directory. If it is None, its value defaults to the directory
    containing ``file``.

    ``remote_data_root`` must be a full URL or None. If it is None, ``file``
    will be checked for a fallback value. "remote_data_root" may be provided in
    the YAML file under the reserved keyword "neurotic_config". Any non-None
    value passed to this function will override the value provided in the file.
    If both are unspecified, it is assumed that no remote data store exists.

    The "data_dir" property is optional for every data set in ``file`` and
    specifies the directory on the local system containing the data files.
    "data_dir" may be an absolute path or a relative path with respect to
    ``local_data_root``. If it is a relative path, it will be converted to an
    absolute path.

    The "remote_data_dir" property is optional for every data set in ``file``
    and specifies the directory on a remote server containing the data files.
    "remote_data_dir" may be a full URL or a relative path with respect to
    ``remote_data_root``. If it is a relative path, it will be converted to a
    full URL.

    File paths (e.g., "data_file", "video_file") are assumed to be relative to
    both "data_dir" and "remote_data_dir" (i.e., the local and remote data
    stores mirror one another) and can be resolved with ``_abs_path`` or
    ``_abs_url``.
    """

    assert file is not None, 'metadata file must be specified'
    assert os.path.exists(file), 'metadata file "{}" cannot be found'.format(file)

    # local_data_root defaults to the directory containing file
    if local_data_root is None:
        local_data_root = os.path.dirname(file)

    # load metadata from file
    with open(file) as f:
        md = yaml.safe_load(f)

    # remove special entry "neurotic_config" from the dict if it exists
    config = md.pop('neurotic_config', None)
    if isinstance(config, dict):
        # process global settings
        remote_data_root_from_file = config.get('remote_data_root', None)
    else:
        # use defaults for all global settings
        remote_data_root_from_file = None

    # use remote_data_root passed to function preferentially
    if remote_data_root is not None:
        if not _is_url(remote_data_root):
            raise ValueError('"remote_data_root" passed to function is not a full URL: "{}"'.format(remote_data_root))
        else:
            # use the value passed to the function
            pass
    elif remote_data_root_from_file is not None:
        if not _is_url(remote_data_root_from_file):
            raise ValueError('"remote_data_root" provided in file is not a full URL: "{}"'.format(remote_data_root_from_file))
        else:
            # use the value provided in the file
            remote_data_root = remote_data_root_from_file
    else:
        # both potential sources of remote_data_root are None
        pass

    # iterate over all data sets
    for key in md:

        assert type(md[key]) is dict, 'File "{}" may be formatted incorrectly, especially beginning with entry "{}"'.format(file, key)

        # fill in missing metadata with default values
        defaults = _defaults_for_key(key)
        for k in defaults:
            md[key].setdefault(k, defaults[k])

        # determine the absolute path of the local data directory
        if md[key]['data_dir'] is not None:
            # data_dir is either an absolute path already or is specified
            # relative to local_data_root
            if os.path.isabs(md[key]['data_dir']):
                dir = md[key]['data_dir']
            else:
                dir = os.path.abspath(os.path.join(local_data_root, md[key]['data_dir']))
        else:
            # data_dir is a required property
            raise ValueError('"data_dir" missing for "{}"'.format(key))
        md[key]['data_dir'] = os.path.normpath(dir)

        # determine the full URL to the remote data directory
        if md[key]['remote_data_dir'] is not None:
            # remote_data_dir is either a full URL already or is specified
            # relative to remote_data_root
            if _is_url(md[key]['remote_data_dir']):
                url = md[key]['remote_data_dir']
            elif _is_url(remote_data_root):
                url = '/'.join([remote_data_root, md[key]['remote_data_dir']])
            else:
                url = None
        else:
            # there is no remote data store
            url = None
        md[key]['remote_data_dir'] = url

    return md


def _defaults_for_key(key):
    """
    Default values for metadata.
    """

    defaults = {
        # store the key with the metadata
        'key': key,

        # description of data set
        'description': None,

        # the path of the directory containing the data on the local system
        # - this may be an absolute or relative path, but not None since data
        #   must be located locally
        # - if it is a relative path, it will be interpreted by _load_metadata
        #   as relative to local_data_root and will be converted to an absolute
        #   path
        'data_dir': '.',

        # the path of the directory containing the data on a remote server
        # - this may be a full URL or a relative path, or None if there exists
        #   no remote data store
        # - if it is a relative path, it will be interpreted by _load_metadata
        #   as relative to remote_data_root and will be converted to a full URL
        'remote_data_dir': None,

        # the ephys data file
        # - path relative to data_dir and remote_data_dir
        'data_file': None,

        # the name of a Neo IO class
        # - this parameter is optional and exists for overriding the IO class
        #   determined automatically from the data file's extension
        'io_class': None,

        # arguments for the Neo IO class
        # - e.g. for AsciiSignalIO, {'delimiter': ',', 'sampling_rate': 1000, 'units': 'mV'}
        'io_args': None,

        # digital filters to apply before analysis and plotting
        # 0 <= highpass <= lowpass < sample_rate/2
        # - e.g. [{'channel': 'Channel A', 'highpass': 0, 'lowpass': 50}, ...]
        'filters': None,

        # the annotations file
        # - path relative to data_dir and remote_data_dir
        'annotations_file': None,

        # the epoch encoder file
        # - path relative to data_dir and remote_data_dir
        'epoch_encoder_file': None,

        # list of labels for epoch encoder
        'epoch_encoder_possible_labels': ['Type 1', 'Type 2', 'Type 3'],

        # list of dicts giving name, channel, units, amplitude window, epoch window, color for each unit
        # - e.g. [{'name': 'Unit X', 'channel': 'Channel A', 'units': 'uV', 'amplitude': [75, 150], 'epoch': 'Type 1', 'color': 'ff0000'}, ...]
        'amplitude_discriminators': None,

        # list of dicts giving name of a spiketrain, start and stop firing rate
        # thresholds in Hz for each burst
        # - 'spiketrain' is required and used to find the appropriate spike
        #   train by name, whereas 'name' is option and is used to name the
        #   Epoch generated by load_dataset, defaults to the spiketrain's name
        #   with ' burst' appended
        # - e.g. [{'spiketrain': 'Unit X', 'name': 'Unit X burst', 'thresholds': [10, 8]}, ...]
        'burst_detectors': None,

        # the output file of a tridesclous spike sorting analysis
        # - path relative to data_dir and remote_data_dir
        'tridesclous_file': None,

        # dict mapping spike ids to lists of channel indices
        # - e.g. {0: ['Channel A'], 1: ['Channel A'], ...} to indicate clusters 0 and 1 are both on channel A
        # - e.g. {0: ['Channel A', 'Channel B'], ...} to indicate cluster 0 is on both channels A and B
        'tridesclous_channels': None,

        # list of lists of spike ids specifying how to merge clusters
        # - e.g. [[0, 1, 2], [3, 4]] to merge clusters 1 and 2 into 0, merge 4 into 3, and discard all others
        # - e.g. [[0], [1], [2], [3], [4]] to keep clusters 0-4 as they are and discard all others
        'tridesclous_merge': None,

        # the video file
        # - path relative to data_dir and remote_data_dir
        'video_file': None,

        # the video time offset in seconds
        'video_offset': None,

        # list of ordered pairs specifying times and durations that the ephys
        # data collection was paused while the video continued recording
        # - e.g. [[60, 10], [120, 10], [240, 10]] for three 10-second pauses
        #   occurring at times 1:00, 2:00, 3:00 according to the daq, which
        #   would correspond to times 1:00, 2:10, 3:20 according to the video
        'video_jumps': None,

        # a factor to multiply the video frame rate by to correct for async
        # error that accumulates over time at a constant rate
        # - a value less than 1 will decrease the frame rate and shift video
        #   events to later times
        # - a value greater than 1 will increase the frame rate and shift video
        #   events to earlier times
        # - a good estimate can be obtained by taking the amount of time
        #   between two events in the video and dividing by the amount of time
        #   between the same two events in the data
        'video_rate_correction': None,

        # list the channels in the order they should be plotted
        # - e.g. [{'channel': 'Channel A', 'ylabel': 'My channel', 'ylim': [-120, 120], 'units': 'uV'}, ...]
        'plots': None,

        # amount of time in seconds to plot initially
        't_width': 40,

        # factor to subtract from each signal before rectification when
        # calculating rectified area under the curve (RAUC)
        # - can be None, 'mean', or 'median'
        'rauc_baseline': None,

        # width of bins in seconds used for calculating rectified area under
        # the curve (RAUC) for signals
        'rauc_bin_duration': 0.1,
    }

    return defaults


def _abs_path(metadata, file):
    """
    Convert the relative path of file to an absolute path using data_dir
    """
    if metadata[file] is None:
        return None
    else:
        return os.path.normpath(os.path.join(metadata['data_dir'], metadata[file]))


def _abs_url(metadata, file):
    """
    Convert the relative path of file to a full URL using remote_data_dir
    """
    if metadata[file] is None or metadata['remote_data_dir'] is None:
        return None
    else:
        file_path = metadata[file].replace(os.sep, '/')
        url = '/'.join([metadata['remote_data_dir'], file_path])
        # url = urllib.parse.unquote(url)
        # url = urllib.parse.quote(url, safe='/:')
        return url


def _is_url(url):
    """
    Returns True only if the parameter begins with the form <scheme>://<netloc>
    """
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def _download_file(metadata, file, **kwargs):
    """
    Download a file.

    See :func:`neurotic.datasets.download.download` for possible keyword
    arguments.
    """

    if not _is_url(metadata['remote_data_dir']):
        logger.critical('metadata[remote_data_dir] is not a full URL')
        return

    if metadata[file]:

        # create directories if necessary
        if not os.path.exists(os.path.dirname(_abs_path(metadata, file))):
            os.makedirs(os.path.dirname(_abs_path(metadata, file)))

        # download the file only if it does not already exist
        download(_abs_url(metadata, file), _abs_path(metadata, file), **kwargs)


def _download_all_data_files(metadata, **kwargs):
    """
    Download all files associated with metadata.

    See :func:`neurotic.datasets.download.download` for possible keyword
    arguments.
    """

    if not _is_url(metadata['remote_data_dir']):
        logger.critical('metadata[remote_data_dir] is not a full URL')
        return

    for file in [k for k in metadata if k.endswith('_file')]:
        _download_file(metadata, file, **kwargs)


def _selector_labels(all_metadata):
    """

    """

    # indicate presence of local data files with symbols
    has_local_data = {}
    for key, metadata in all_metadata.items():
        filenames = [k for k in metadata if k.endswith('_file') and metadata[k] is not None]
        files_exist = [os.path.exists(_abs_path(metadata, file)) for file in filenames]
        if all(files_exist):
            has_local_data[key] = '◆'
        elif any(files_exist):
            has_local_data[key] = '⬖'
        else:
            has_local_data[key] = '◇'

    # indicate lack of video_offset with an exclamation point unless there is
    # no video_file
    has_video_offset = {}
    for key, metadata in all_metadata.items():
        if metadata['video_offset'] is None and metadata['video_file'] is not None:
            has_video_offset[key] = '!'
        else:
            has_video_offset[key] = ' '

    # create display text for the selector from keys and descriptions
    longest_key_length = max([len(k) for k in all_metadata.keys()])
    labels = [
        has_local_data[k] +
        has_video_offset[k] +
        ' ' +
        k.ljust(longest_key_length + 4) +
        str(all_metadata[k]['description']
            if all_metadata[k]['description'] else '')

        for k in all_metadata.keys()]

    return labels
