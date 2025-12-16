from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfWebLinkAnnotationWidget(PdfUriAnnotationWidget):
    """
    Represents the loaded web link annotation class.
    """

    def ObjectID(self) -> int:
        """
        Represents the Form field identifier.
        """
        GetDllLibPdf().PdfWebLinkAnnotationWidget_ObjectID.argtypes = [c_void_p]
        GetDllLibPdf().PdfWebLinkAnnotationWidget_ObjectID.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfWebLinkAnnotationWidget_ObjectID,self.Ptr)
        return ret