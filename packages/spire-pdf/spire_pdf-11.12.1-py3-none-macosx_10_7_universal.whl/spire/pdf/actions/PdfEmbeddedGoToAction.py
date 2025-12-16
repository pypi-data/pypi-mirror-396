from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfEmbeddedGoToAction(PdfAction):
    """
    Represents an embedded go-to action which allows jumping to or from a PDF file that is embedded in another PDF file.
    """

    @dispatch
    def __init__(self, filename: str, dest: PdfDestination, newWindow: bool):
        """
        Initializes a new instance of the PdfEmbeddedGoToAction class.

        Args:
            filename (str): The target document filename.
            dest (PdfDestination): The destination in the target document to jump to.
            newWindow (bool): Indicates if the target document should be opened in a new window.
        """
        ptrDest: c_void_p = dest.Ptr

        GetDllLibPdf().PdfEmbeddedGoToAction_CreatePdfEmbeddedGoToActionFDN.argtypes = [c_wchar_p, c_void_p, c_bool]
        GetDllLibPdf().PdfEmbeddedGoToAction_CreatePdfEmbeddedGoToActionFDN.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfEmbeddedGoToAction_CreatePdfEmbeddedGoToActionFDN,filename, ptrDest, newWindow)
        super(PdfEmbeddedGoToAction, self).__init__(intPtr)

    @property
    def IsNewWindow(self) -> bool:
        """
        Gets or sets a value indicating whether the target document should be opened in a new window.

        Returns:
            bool: True if the target document should be opened in a new window, otherwise False.
        """
        GetDllLibPdf().PdfEmbeddedGoToAction_get_IsNewWindow.argtypes = [c_void_p]
        GetDllLibPdf().PdfEmbeddedGoToAction_get_IsNewWindow.restype = c_bool
        ret = CallCFunction(GetDllLibPdf().PdfEmbeddedGoToAction_get_IsNewWindow,self.Ptr)
        return ret

    @IsNewWindow.setter
    def IsNewWindow(self, value: bool):
        """
        Sets a value indicating whether the target document should be opened in a new window.

        Args:
            value (bool): True if the target document should be opened in a new window, otherwise False.
        """
        GetDllLibPdf().PdfEmbeddedGoToAction_set_IsNewWindow.argtypes = [c_void_p, c_bool]
        CallCFunction(GetDllLibPdf().PdfEmbeddedGoToAction_set_IsNewWindow,self.Ptr, value)

    @property
    def FileName(self) -> str:
        """
        Gets or sets the target document name.

        Returns:
            str: The target document name.
        """
        GetDllLibPdf().PdfEmbeddedGoToAction_get_FileName.argtypes = [c_void_p]
        GetDllLibPdf().PdfEmbeddedGoToAction_get_FileName.restype = c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPdf().PdfEmbeddedGoToAction_get_FileName,self.Ptr))
        return ret

    @FileName.setter
    def FileName(self, value: str):
        """
        Sets the target document name.

        Args:
            value (str): The target document name.
        """
        GetDllLibPdf().PdfEmbeddedGoToAction_set_FileName.argtypes = [c_void_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfEmbeddedGoToAction_set_FileName,self.Ptr, value)

    @property
    def Destination(self) -> 'PdfDestination':
        """
        Gets or sets the destination in the target document to jump to.

        Returns:
            PdfDestination: The destination in the target document to jump to.
        """
        GetDllLibPdf().PdfEmbeddedGoToAction_get_Destination.argtypes = [c_void_p]
        GetDllLibPdf().PdfEmbeddedGoToAction_get_Destination.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfEmbeddedGoToAction_get_Destination,self.Ptr)
        ret = None if intPtr == None else PdfDestination(intPtr)
        return ret