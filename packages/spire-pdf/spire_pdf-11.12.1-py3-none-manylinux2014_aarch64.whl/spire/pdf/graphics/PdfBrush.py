from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfBrush(SpireObject):
    """
    Represents the abstract brush, which contains the basic functionality of a brush.
    """

    def Clone(self) -> 'PdfBrush':
        """
        Creates a new copy of a brush.

        Returns:
            A new instance of the Brush class.
        """
        GetDllLibPdf().PdfBrush_Clone.argtypes = [c_void_p]
        GetDllLibPdf().PdfBrush_Clone.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfBrush_Clone,self.Ptr)
        ret = None if intPtr == None else PdfBrush(intPtr)
        return ret