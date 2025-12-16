from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfStateFieldWidget(PdfStyledFieldWidget):
    """
    Represents the base class for loaded state field.
    """

    @property
    def WidgetItems(self) -> 'PdfStateWidgetItemCollection':
        """
        Gets the items collection.
        """
        GetDllLibPdf().PdfStateFieldWidget_get_WidgetItems.argtypes = [c_void_p]
        GetDllLibPdf().PdfStateFieldWidget_get_WidgetItems.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfStateFieldWidget_get_WidgetItems,self.Ptr)
        ret = None if intPtr == None else PdfStateWidgetItemCollection(intPtr)
        return ret

    def ObjectID(self) -> int:
        """
        Form field identifier
        """
        GetDllLibPdf().PdfStateFieldWidget_ObjectID.argtypes = [c_void_p]
        GetDllLibPdf().PdfStateFieldWidget_ObjectID.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfStateFieldWidget_ObjectID,self.Ptr)
        return ret