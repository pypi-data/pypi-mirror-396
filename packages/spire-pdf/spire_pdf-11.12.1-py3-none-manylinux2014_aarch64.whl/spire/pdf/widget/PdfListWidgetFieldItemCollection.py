from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfListWidgetFieldItemCollection(PdfCollection):
    """
    Represents loaded item collection.
    """

    def get_Item(self, index: int) -> 'PdfListFieldWidgetItem':
        """
        Gets the item at the specified index.
        """
        
        GetDllLibPdf().PdfListWidgetFieldItemCollection_get_Item.argtypes = [c_void_p, c_int]
        GetDllLibPdf().PdfListWidgetFieldItemCollection_get_Item.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfListWidgetFieldItemCollection_get_Item,self.Ptr, index)
        ret = None if intPtr == None else PdfListFieldWidgetItem(intPtr)
        return ret