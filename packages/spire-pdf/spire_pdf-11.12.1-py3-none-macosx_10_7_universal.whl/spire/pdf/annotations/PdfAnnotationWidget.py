from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfAnnotationWidget(PdfAnnotation):
    """
    Represents the base class for loaded annotation classes.
    """

    @property
    def PageWidget(self) -> 'PdfPageBase':
        """
        Gets and sets the Page.
        """
        GetDllLibPdf().PdfAnnotationWidget_get_PageWidget.argtypes = [c_void_p]
        GetDllLibPdf().PdfAnnotationWidget_get_PageWidget.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfAnnotationWidget_get_PageWidget,self.Ptr)
        ret = None if intPtr == None else PdfPageBase(intPtr)
        return ret

    @PageWidget.setter
    def PageWidget(self, value: 'PdfPageBase'):
        """
        Sets the Page.
        """
        GetDllLibPdf().PdfAnnotationWidget_set_PageWidget.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfAnnotationWidget_set_PageWidget,self.Ptr, value.Ptr)

    def SetText(self, text: str):
        """
        Sets the name of the field.
        """
        GetDllLibPdf().PdfAnnotationWidget_SetText.argtypes = [c_void_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfAnnotationWidget_SetText,self.Ptr, text)

    def ObjectID(self) -> int:
        """
        Represents the Form field identifier.
        """
        GetDllLibPdf().PdfAnnotationWidget_ObjectID.argtypes = [c_void_p]
        GetDllLibPdf().PdfAnnotationWidget_ObjectID.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfAnnotationWidget_ObjectID,self.Ptr)
        return ret