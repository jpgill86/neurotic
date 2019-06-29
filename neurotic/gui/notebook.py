# -*- coding: utf-8 -*-
"""

"""

try:
    import ipywidgets
    from IPython.display import HTML
    HAVE_IPYWIDGETS = True
except ImportError:
    HAVE_IPYWIDGETS = False

from ..datasets import MetadataManager, selector_labels


class MetadataSelector(MetadataManager):
    """
    Interactive list box for Jupyter notebooks that allows the user to select
    which metadata set they would like to work with.

    >>> metadata = MetadataSelector(file='metadata.yml')
    >>> display(metadata)

    After clicking on an item in the list, the selected metadata set is
    accessible at `metadata.selected_metadata`, e.g.

    >>> metadata.selected_metadata['data_file']

    A compact indexing method is implemented that allows the selected metadata
    set to be accessed directly, e.g.

    >>> metadata['data_file']

    This allows the MetadataSelector to be passed to functions expecting a
    simple dictionary corresponding to a single metadata set, and the selected
    metadata set will be used automatically.
    """

    def __init__(self, file=None, local_data_root=None, remote_data_root=None, initial_selection=None):
        """
        Initialize a new MetadataSelector.
        """

        assert HAVE_IPYWIDGETS, 'ipywidgets is a requirement for MetadataSelector'

        # load the metadata and set the initial selection
        MetadataManager.__init__(
            self,
            file=file,
            local_data_root=local_data_root,
            remote_data_root=remote_data_root,
            initial_selection=initial_selection)

        # create a widget container which will be displayed whenever the
        # MetadataSelector is displayed
        self.main_widget = ipywidgets.VBox()
        self._ipython_display_ = self.main_widget._ipython_display_

        # create the selector widget
        self.selector = ipywidgets.Select()

        if self.all_metadata is not None:
            # create display text for the selector from keys and descriptions
            self.selector.options = zip(selector_labels(self.all_metadata), self.all_metadata.keys())

            # set initial selection
            if self._selection is None:
                self.selector.value = list(self.all_metadata)[0]
            else:
                self.selector.value = self._selection

        # use monospace font for items in the selector
        self.selector.add_class('metadata-selector')
        try:
            display(HTML('<style>.metadata-selector select {font-family: monospace;}</style>'))
        except NameError:
            # likely operating outside Jupyter notebook
            pass

        # set other selector display options
        self.selector.description = 'Data set:'
        self.selector.rows = 20
        self.selector.layout = ipywidgets.Layout(width = '99%')
        self.selector.style = {'description_width': 'initial'}

        # configure the _on_select function to be called whenever the selection changes
        self.selector.observe(self._on_select, names = 'value')
        if self.all_metadata is not None:
            self._on_select({'new': self.selector.value}) # run now on initial selection

        # create the reload button
        self.reload_button = ipywidgets.Button(icon='refresh', description='Reload', layout=ipywidgets.Layout(height='auto'), disabled=False)
        self.reload_button.on_click(self._on_reload_clicked)

        # create the download button
        self.download_button = ipywidgets.Button(icon='download', description='Download', layout=ipywidgets.Layout(height='auto'), disabled=False)
        self.download_button.on_click(self._on_download_clicked)

        # populate the box
        # self.main_widget.children = [self.selector, self.reload_button, self.download_button]
        self.main_widget.children = [self.selector, self.reload_button]

    def _on_select(self, change):
        """
        Run each time the selection changes.
        """
        self._selection = self.selector.value

        # warn if video_offset is not set
        if self.selected_metadata['video_file'] is not None and self.selected_metadata['video_offset'] is None:
            print('Warning: Video sync may be incorrect! video_offset not set for {}'.format(self._selection))

    def _on_reload_clicked(self, button):
        """
        Run each time the reload button is clicked.
        """
        self.load()

        if self.all_metadata is not None:
            # remember the current selection
            old_selection = self._selection

            # changing the options triggers the selection to change
            self.selector.options = zip(selector_labels(self.all_metadata), self.all_metadata.keys())

            # reselect the original selection if it still exists
            if old_selection in self.all_metadata:
                self.selector.value = old_selection

    def _on_download_clicked(self, button):
        """
        Run each time the download button is clicked.
        """
        self.download_all_data_files()
