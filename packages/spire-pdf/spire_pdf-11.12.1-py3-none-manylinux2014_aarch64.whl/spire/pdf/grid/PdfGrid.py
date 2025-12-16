from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfGrid(PdfLayoutWidget):
    """
    Represents a grid in a PDF document.
    """
    @dispatch
    def __init__(self):
        GetDllLibPdf().PdfGrid_CreatePdfGrid.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfGrid_CreatePdfGrid)
        super(PdfGrid, self).__init__(intPtr)

    @property
    def Headers(self) -> 'PdfGridHeaderCollection':
        """
        Gets the headers.
        """
        GetDllLibPdf().PdfGrid_get_Headers.argtypes = [c_void_p]
        GetDllLibPdf().PdfGrid_get_Headers.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfGrid_get_Headers,self.Ptr)
        ret = None if intPtr == None else PdfGridHeaderCollection(intPtr)
        return ret

    @property
    def Rows(self) -> 'PdfGridRowCollection':
        """
        Gets the rows.
        """
        GetDllLibPdf().PdfGrid_get_Rows.argtypes = [c_void_p]
        GetDllLibPdf().PdfGrid_get_Rows.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfGrid_get_Rows,self.Ptr)
        ret = None if intPtr == None else PdfGridRowCollection(intPtr)
        return ret

    @property
    def DataSource(self) -> 'SpireObject':
        """
        Gets or sets the data source.
        """
        GetDllLibPdf().PdfGrid_get_DataSource.argtypes = [c_void_p]
        GetDllLibPdf().PdfGrid_get_DataSource.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfGrid_get_DataSource,self.Ptr)
        ret = None if intPtr == None else SpireObject(intPtr)
        return ret

    @DataSource.setter
    def DataSource(self, value: 'SpireObject'):
        GetDllLibPdf().PdfGrid_set_DataSource.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfGrid_set_DataSource,self.Ptr, value.Ptr)

    @property
    def DataMember(self) -> str:
        """
        Gets or sets the data member.
        """
        GetDllLibPdf().PdfGrid_get_DataMember.argtypes = [c_void_p]
        GetDllLibPdf().PdfGrid_get_DataMember.restype = c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPdf().PdfGrid_get_DataMember,self.Ptr))
        return ret

    @DataMember.setter
    def DataMember(self, value: str):
        GetDllLibPdf().PdfGrid_set_DataMember.argtypes = [c_void_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfGrid_set_DataMember,self.Ptr, value)

    @property
    def Style(self) -> 'PdfGridStyle':
        """
        Gets or sets the style.
        """
        GetDllLibPdf().PdfGrid_get_Style.argtypes = [c_void_p]
        GetDllLibPdf().PdfGrid_get_Style.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfGrid_get_Style,self.Ptr)
        ret = None if intPtr == None else PdfGridStyle(intPtr)
        return ret

    @Style.setter
    def Style(self, value: 'PdfGridStyle'):
        GetDllLibPdf().PdfGrid_set_Style.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfGrid_set_Style,self.Ptr, value.Ptr)

    @property
    def Columns(self) -> 'PdfGridColumnCollection':
        """
        Gets the columns.
        """
        GetDllLibPdf().PdfGrid_get_Columns.argtypes = [c_void_p]
        GetDllLibPdf().PdfGrid_get_Columns.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfGrid_get_Columns,self.Ptr)
        ret = None if intPtr == None else PdfGridColumnCollection(intPtr)
        return ret
