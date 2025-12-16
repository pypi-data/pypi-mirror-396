from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfButtonWidgetItemCollection(PdfCollection):
    """
    Represents a collection of button items.
    """

    def get_Item(self, index: int) -> 'PdfButtonWidgetWidgetItem':
        """
        Gets the button item at the specified index.
        """
        
        GetDllLibPdf().PdfButtonWidgetItemCollection_get_Item.argtypes = [c_void_p, c_int]
        GetDllLibPdf().PdfButtonWidgetItemCollection_get_Item.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfButtonWidgetItemCollection_get_Item,self.Ptr, index)
        ret = None if intPtr == None else PdfButtonWidgetWidgetItem(intPtr)
        return ret