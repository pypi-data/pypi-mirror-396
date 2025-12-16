# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args

ComponentType = typing.Union[
    str,
    int,
    float,
    Component,
    None,
    typing.Sequence[typing.Union[str, int, float, Component, None]],
]

NumberType = typing.Union[
    typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
]


class DashUploaderUppy5(Component):
    """A DashUploaderUppy5 component.
A dash Component.

Keyword arguments:

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- allowMultipleUploadBatches (boolean | number | string | dict | list; optional):
    Whether to allow several upload batches. Default: `True`.

- allowedFileTypes (list of strings; optional):
    Wildcards `image/*`, or exact mime types `image/jpeg`,  or file
    extensions `.jpg`.

- autoProceed (boolean | number | string | dict | list; optional):
    If `True`, it will upload as soon as files are added.

- disableThumbnailGenerator (boolean | number | string | dict | list; optional):
    Disable the thumbnail generator completely.

- disabled (boolean | number | string | dict | list; optional):
    Enabling this option makes the Dashboard grayed-out and
    non-interactive.

- failedFiles (boolean | number | string | dict | list; optional)

- fileManagerSelectionType (string; optional):
    Configure the type of selections allowed when browsing your file
    system via the file manager selection window.  It only can be one
    of the string ('files', 'folders' and 'both').

- hideProgressDetails (boolean | number | string | dict | list; optional):
    Show or hide progress details in the status bar.

- maxFileSize (number; optional):
    Maximum file size in bytes for each individual file.

- maxNumberOfFiles (number; optional):
    Total number of files that can be selected.

- maxTotalFileSize (number; optional):
    Maximum file size in bytes for all the files  that can be selected
    for upload.

- minFileSize (number; optional):
    Minimum file size in bytes for each individual file.

- minNumberOfFiles (number; optional):
    Minimum number of files that must be selected before the upload.

- note (string; optional):
    A string of text to be placed in the Dashboard UI.

- showSelectedFiles (boolean | number | string | dict | list; optional):
    Show the list of added files with a preview and file information.

- singleFileFullScreen (boolean | number | string | dict | list; optional):
    When only one file is selected, its preview and meta information
    will be centered and enlarged.

- size (boolean | number | string | dict | list; optional):
    Size of the Dashboard in pixels or percentages.

- theme (string; optional):
    Light or dark theme for the Dashboard.  When it is set to `auto`,
    it will respect the user’s system settings and switch
    automatically.  It only can be one of the string ('light', 'dark'
    and 'auto').

- uploadId (string; optional):
    The unique identifier for the upload session.  This will be sent
    to the backend to create a specific sub-folder.

- uploadUrl (string; required):
    URL of the HTTP server.

- uploadedFiles (boolean | number | string | dict | list; optional):
    List of successfully uploaded files.

- waitForThumbnailsBeforeUpload (boolean | number | string | dict | list; optional):
    Whether to wait for all thumbnails to be ready before starting the
    upload."""
    _children_props: typing.List[str] = []
    _base_nodes = ['children']
    _namespace = 'dash_uploader_uppy5'
    _type = 'DashUploaderUppy5'


    def __init__(
        self,
        uploadUrl: typing.Optional[str] = None,
        autoProceed: typing.Optional[typing.Any] = None,
        allowMultipleUploadBatches: typing.Optional[typing.Any] = None,
        maxFileSize: typing.Optional[typing.Union[NumberType]] = None,
        minFileSize: typing.Optional[typing.Union[NumberType]] = None,
        maxTotalFileSize: typing.Optional[typing.Union[NumberType]] = None,
        maxNumberOfFiles: typing.Optional[typing.Union[NumberType]] = None,
        minNumberOfFiles: typing.Optional[typing.Union[NumberType]] = None,
        allowedFileTypes: typing.Optional[typing.Union[typing.Sequence[str]]] = None,
        uploadId: typing.Optional[typing.Union[str]] = None,
        disabled: typing.Optional[typing.Any] = None,
        theme: typing.Optional[typing.Union[str]] = None,
        note: typing.Optional[typing.Union[str]] = None,
        size: typing.Optional[typing.Any] = None,
        hideProgressDetails: typing.Optional[typing.Any] = None,
        disableThumbnailGenerator: typing.Optional[typing.Any] = None,
        waitForThumbnailsBeforeUpload: typing.Optional[typing.Any] = None,
        showSelectedFiles: typing.Optional[typing.Any] = None,
        singleFileFullScreen: typing.Optional[typing.Any] = None,
        fileManagerSelectionType: typing.Optional[typing.Union[str]] = None,
        uploadedFiles: typing.Optional[typing.Any] = None,
        failedFiles: typing.Optional[typing.Any] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'allowMultipleUploadBatches', 'allowedFileTypes', 'autoProceed', 'disableThumbnailGenerator', 'disabled', 'failedFiles', 'fileManagerSelectionType', 'hideProgressDetails', 'maxFileSize', 'maxNumberOfFiles', 'maxTotalFileSize', 'minFileSize', 'minNumberOfFiles', 'note', 'showSelectedFiles', 'singleFileFullScreen', 'size', 'theme', 'uploadId', 'uploadUrl', 'uploadedFiles', 'waitForThumbnailsBeforeUpload']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'allowMultipleUploadBatches', 'allowedFileTypes', 'autoProceed', 'disableThumbnailGenerator', 'disabled', 'failedFiles', 'fileManagerSelectionType', 'hideProgressDetails', 'maxFileSize', 'maxNumberOfFiles', 'maxTotalFileSize', 'minFileSize', 'minNumberOfFiles', 'note', 'showSelectedFiles', 'singleFileFullScreen', 'size', 'theme', 'uploadId', 'uploadUrl', 'uploadedFiles', 'waitForThumbnailsBeforeUpload']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        for k in ['uploadUrl']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(DashUploaderUppy5, self).__init__(**args)

setattr(DashUploaderUppy5, "__init__", _explicitize_args(DashUploaderUppy5.__init__))
