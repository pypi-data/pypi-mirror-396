from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfGridCellContentList(SpireObject):
    """
    A collection of PdfGridCellContent classes.
    """

    # @property
    # def List(self) -> 'IList1':
    #     """
    #
    #     """
    #     GetDllLibPdf().PdfGridCellContentList_get_List.argtypes = [c_void_p]
    #     GetDllLibPdf().PdfGridCellContentList_get_List.restype = c_void_p
    #     intPtr = CallCFunction(GetDllLibPdf().PdfGridCellContentList_get_List,self.Ptr)
    #     ret = None if intPtr == None else IList1(intPtr)
    #     return ret