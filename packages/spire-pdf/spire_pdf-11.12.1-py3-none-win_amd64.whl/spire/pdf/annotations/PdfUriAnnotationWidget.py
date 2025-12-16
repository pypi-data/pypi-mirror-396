from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfUriAnnotationWidget(PdfStyledAnnotationWidget):
    """
    Represents the loaded unique resource identifier annotation class.
    """

    @property
    def Uri(self) -> str:
        """
        Gets or sets the unique resource identifier text of the annotation.
        """
        GetDllLibPdf().PdfUriAnnotationWidget_get_Uri.argtypes = [c_void_p]
        GetDllLibPdf().PdfUriAnnotationWidget_get_Uri.restype = c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPdf().PdfUriAnnotationWidget_get_Uri,self.Ptr))
        return ret

    @Uri.setter
    def Uri(self, value: str):
        """
        Sets the unique resource identifier text of the annotation.
        """
        GetDllLibPdf().PdfUriAnnotationWidget_set_Uri.argtypes = [c_void_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfUriAnnotationWidget_set_Uri,self.Ptr, value)

    def ObjectID(self) -> int:
        """
        Represents the Form field identifier.
        """
        GetDllLibPdf().PdfUriAnnotationWidget_ObjectID.argtypes = [c_void_p]
        GetDllLibPdf().PdfUriAnnotationWidget_ObjectID.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfUriAnnotationWidget_ObjectID,self.Ptr)
        return ret