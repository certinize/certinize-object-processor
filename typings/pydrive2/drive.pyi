"""
This type stub file was generated by pyright.
"""

from .apiattr import ApiAttributeMixin
from .auth import LoadAuth

class GoogleDrive(ApiAttributeMixin):
    """Main Google Drive class."""
    def __init__(self, auth=...) -> None:
        """Create an instance of GoogleDrive.

        :param auth: authorized GoogleAuth instance.
        :type auth: pydrive2.auth.GoogleAuth.
        """
        ...
    
    def CreateFile(self, metadata=...): # -> GoogleDriveFile:
        """Create an instance of GoogleDriveFile with auth of this instance.

        This method would not upload a file to GoogleDrive.

        :param metadata: file resource to initialize GoogleDriveFile with.
        :type metadata: dict.
        :returns: pydrive2.files.GoogleDriveFile -- initialized with auth of this
                  instance.
        """
        ...
    
    def ListFile(self, param=...): # -> GoogleDriveFileList:
        """Create an instance of GoogleDriveFileList with auth of this instance.

        This method will not fetch from Files.List().

        :param param: parameter to be sent to Files.List().
        :type param: dict.
        :returns: pydrive2.files.GoogleDriveFileList -- initialized with auth of
                  this instance.
        """
        ...
    
    @LoadAuth
    def GetAbout(self):
        """Return information about the Google Drive of the auth instance.

        :returns: A dictionary of Google Drive information like user, usage, quota etc.
        """
        ...
    


