from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfTextAnnotationWidget(PdfMarkUpAnnotationWidget):
    """
    Represents a PDF text annotation widget.
    """

    def ObjectID(self) -> int:
        """
        Returns the form field identifier.
        """
        GetDllLibPdf().PdfTextAnnotationWidget_ObjectID.argtypes = [c_void_p]
        GetDllLibPdf().PdfTextAnnotationWidget_ObjectID.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfTextAnnotationWidget_ObjectID,self.Ptr)
        return ret