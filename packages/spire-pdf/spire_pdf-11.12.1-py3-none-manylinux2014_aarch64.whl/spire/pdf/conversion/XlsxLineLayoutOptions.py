from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class XlsxLineLayoutOptions(XlsxOptions):
    """
    XlsxLineLayoutOptions class for PDF to Excel conversion with line layout options.
    """
    @dispatch
    def __init__(self):
        """
        Initializes a new instance of the XlsxLineLayoutOptions class.
        """
        GetDllLibPdf().XlsxLineLayoutOptions_CreateXlsxLineLayoutOptions.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().XlsxLineLayoutOptions_CreateXlsxLineLayoutOptions)
        super(XlsxLineLayoutOptions, self).__init__(intPtr)

    @dispatch
    def __init__(self, convertToMultipleSheet: bool, rotatedText: bool, splitCell: bool):
        """
        Initializes a new instance of the XlsxLineLayoutOptions class with specified options.

        Args:
            convertToMultipleSheet (bool): Indicates whether to convert to multiple sheets.
            rotatedText (bool): Indicates whether to rotate the text.
            splitCell (bool): Indicates whether to split the cell.
        """
        GetDllLibPdf().XlsxLineLayoutOptions_CreateXlsxLineLayoutOptionsCRS.argtypes = [c_bool, c_bool, c_bool]
        GetDllLibPdf().XlsxLineLayoutOptions_CreateXlsxLineLayoutOptionsCRS.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().XlsxLineLayoutOptions_CreateXlsxLineLayoutOptionsCRS,convertToMultipleSheet, rotatedText, splitCell)
        super(XlsxLineLayoutOptions, self).__init__(intPtr)

    @dispatch
    def __init__(self, convertToMultipleSheet: bool, rotatedText: bool, splitCell: bool, wrapText: bool):
        """
        Initializes a new instance of the XlsxLineLayoutOptions class with specified options.

        Args:
            convertToMultipleSheet (bool): Indicates whether to convert to multiple sheets.
            rotatedText (bool): Indicates whether to rotate the text.
            splitCell (bool): Indicates whether to split the cell.
            wrapText (bool): Indicates whether to wrap the text.
        """
        GetDllLibPdf().XlsxLineLayoutOptions_CreateXlsxLineLayoutOptionsCRSW.argtypes = [c_bool, c_bool, c_bool, c_bool]
        GetDllLibPdf().XlsxLineLayoutOptions_CreateXlsxLineLayoutOptionsCRSW.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().XlsxLineLayoutOptions_CreateXlsxLineLayoutOptionsCRSW,convertToMultipleSheet, rotatedText, splitCell, wrapText)
        super(XlsxLineLayoutOptions, self).__init__(intPtr)

    @dispatch
    def __init__(self, convertToMultipleSheet: bool, rotatedText: bool, splitCell: bool, wrapText: bool, overlapText: bool):
        """
        Initializes a new instance of the XlsxLineLayoutOptions class with specified options.

        Args:
            convertToMultipleSheet (bool): Indicates whether to convert to multiple sheets.
            rotatedText (bool): Indicates whether to rotate the text.
            splitCell (bool): Indicates whether to split the cell.
            wrapText (bool): Indicates whether to wrap the text.
            overlapText (bool): Indicates whether to overlap the text.
        """
        GetDllLibPdf().XlsxLineLayoutOptions_CreateXlsxLineLayoutOptionsCRSWO.argtypes = [c_bool, c_bool, c_bool, c_bool, c_bool]
        GetDllLibPdf().XlsxLineLayoutOptions_CreateXlsxLineLayoutOptionsCRSWO.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().XlsxLineLayoutOptions_CreateXlsxLineLayoutOptionsCRSWO,convertToMultipleSheet, rotatedText, splitCell, wrapText, overlapText)
        super(XlsxLineLayoutOptions, self).__init__(intPtr)

