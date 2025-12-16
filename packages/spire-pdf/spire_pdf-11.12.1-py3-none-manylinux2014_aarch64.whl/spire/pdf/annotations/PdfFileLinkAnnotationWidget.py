from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfFileLinkAnnotationWidget(PdfStyledAnnotationWidget):
    """
    Represents the loaded file link annotation class.
    """

    @property
    def FileName(self) -> str:
        """
        Gets or sets the filename of the annotation.
        """
        GetDllLibPdf().PdfFileLinkAnnotationWidget_get_FileName.argtypes = [c_void_p]
        GetDllLibPdf().PdfFileLinkAnnotationWidget_get_FileName.restype = c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPdf().PdfFileLinkAnnotationWidget_get_FileName,self.Ptr))
        return ret

    @FileName.setter
    def FileName(self, value: str):
        """
        Sets the filename of the annotation.
        """
        GetDllLibPdf().PdfFileLinkAnnotationWidget_set_FileName.argtypes = [c_void_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfFileLinkAnnotationWidget_set_FileName,self.Ptr, value)

    def ObjectID(self) -> int:
        """
        Represents the Form field identifier.
        """
        GetDllLibPdf().PdfFileLinkAnnotationWidget_ObjectID.argtypes = [c_void_p]
        GetDllLibPdf().PdfFileLinkAnnotationWidget_ObjectID.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfFileLinkAnnotationWidget_ObjectID,self.Ptr)
        return ret