class MondayAPIError(Exception):
    """Base class for exceptions in MondayAPI module."""

class TokenMissingError(MondayAPIError):
    """Invalid or Missing __TOKEN__ file"""
    def __init__(self):
        super().__init__('No __TOKEN__ file was found. New file was created. '
                         'Please add your token to the file and try again.')

class TokenEmptyError(MondayAPIError):
    """Empty __TOKEN__ file"""
    def __init__(self):
        super().__init__('__TOKEN__ file was found but empty. '
                         'Please add your token to the file and try again.')
