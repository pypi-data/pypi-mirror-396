from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfRubberStampAnnotationWidget(PdfMarkUpAnnotationWidget):
    """
    Represents the loaded rubber stamp annotation class.
    """

    @property
    def Icon(self) -> 'PdfRubberStampAnnotationIcon':
        """
        Gets or sets the icon of the annotation.
        """
        GetDllLibPdf().PdfRubberStampAnnotationWidget_get_Icon.argtypes = [c_void_p]
        GetDllLibPdf().PdfRubberStampAnnotationWidget_get_Icon.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfRubberStampAnnotationWidget_get_Icon,self.Ptr)
        objwrapped = PdfRubberStampAnnotationIcon(ret)
        return objwrapped

    @Icon.setter
    def Icon(self, value: 'PdfRubberStampAnnotationIcon'):
        """
        Sets the icon of the annotation.
        """
        GetDllLibPdf().PdfRubberStampAnnotationWidget_set_Icon.argtypes = [c_void_p, c_int]
        CallCFunction(GetDllLibPdf().PdfRubberStampAnnotationWidget_set_Icon,self.Ptr, value.value)

    def ObjectID(self) -> int:
        """
        Represents the Form field identifier.
        """
        GetDllLibPdf().PdfRubberStampAnnotationWidget_ObjectID.argtypes = [c_void_p]
        GetDllLibPdf().PdfRubberStampAnnotationWidget_ObjectID.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfRubberStampAnnotationWidget_ObjectID,self.Ptr)
        return ret