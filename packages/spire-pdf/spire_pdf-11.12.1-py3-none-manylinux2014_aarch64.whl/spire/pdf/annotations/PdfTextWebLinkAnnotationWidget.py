from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfTextWebLinkAnnotationWidget(PdfStyledAnnotationWidget):
    """
    Represents the loaded text web link annotation class.
    """

    @property
    def Url(self) -> str:
        """
        Gets or sets the Url.
        """
        GetDllLibPdf().PdfTextWebLinkAnnotationWidget_get_Url.argtypes = [c_void_p]
        GetDllLibPdf().PdfTextWebLinkAnnotationWidget_get_Url.restype = c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPdf().PdfTextWebLinkAnnotationWidget_get_Url,self.Ptr))
        return ret

    @Url.setter
    def Url(self, value: str):
        """
        Sets the Url.
        """
        GetDllLibPdf().PdfTextWebLinkAnnotationWidget_set_Url.argtypes = [c_void_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfTextWebLinkAnnotationWidget_set_Url,self.Ptr, value)

    def ObjectID(self) -> int:
        """
        Represents the Form field identifier.
        """
        GetDllLibPdf().PdfTextWebLinkAnnotationWidget_ObjectID.argtypes = [c_void_p]
        GetDllLibPdf().PdfTextWebLinkAnnotationWidget_ObjectID.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfTextWebLinkAnnotationWidget_ObjectID,self.Ptr)
        return ret