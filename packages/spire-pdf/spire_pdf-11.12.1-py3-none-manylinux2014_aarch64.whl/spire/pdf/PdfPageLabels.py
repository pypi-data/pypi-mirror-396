from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfPageLabels(SpireObject):
    """
    Represents the document's labeling ranges.
    """

    @dispatch
    def __init__(self):
        GetDllLibPdf().PdfPageLabels_CreatePdfPageLabels.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageLabels_CreatePdfPageLabels)
        super(PdfPageLabels, self).__init__(intPtr)

    @dispatch
    def AddRange(self, indexOfFirstPage: int, numberStyle: str, prefix: str):
        """
        Adds a labeling range which is a series of consecutive pages using the same numbering system.

        Args:
            indexOfFirstPage: The page index of the first page in the labeling range.
            numberStyle: The numbering style to be used for the numeric portion of each page label.
                Options: Decimal_Arabic_Numerals/Uppercase_Roman_Numerals/Lowercase_Roman_Numerals/Uppercase_Letters/Lowercase_Letters
            prefix: The label prefix for page labels in the labeling range.
        """
        GetDllLibPdf().PdfPageLabels_AddRange.argtypes = [c_void_p, c_int, c_wchar_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfPageLabels_AddRange,self.Ptr, indexOfFirstPage, numberStyle, prefix)

    @dispatch
    def AddRange(self, indexOfFirstPage: int, numberStyle: str, prefix: str, numberOfFirstPage: int):
        """
        Adds a labeling range which is a series of consecutive pages using the same numbering system.

        Args:
            indexOfFirstPage: The page index of the first page in the labeling range.
            numberStyle: The numbering style to be used for the numeric portion of each page label.
                Options: Decimal_Arabic_Numerals/Uppercase_Roman_Numerals/Lowercase_Roman_Numerals/Uppercase_Letters/Lowercase_Letters
            prefix: The label prefix for page labels in the labeling range.
            numberOfFirstPage: The value of the numeric portion for the first page label in the range.
                Subsequent pages are numbered sequentially from this value, which must be greater than or equal to 1.
                Default value: 1.
        """
        GetDllLibPdf().PdfPageLabels_AddRangeINPN.argtypes = [c_void_p, c_int, c_wchar_p, c_wchar_p, c_int]
        CallCFunction(GetDllLibPdf().PdfPageLabels_AddRangeINPN,self.Ptr, indexOfFirstPage, numberStyle, prefix, numberOfFirstPage)

    def GetPageLabel(self, index: int) -> str:
        """
        Gets the page label.

        Args:
            index: The page index.

        Returns:
            The page label.
        """
        GetDllLibPdf().PdfPageLabels_GetPageLabel.argtypes = [c_void_p, c_int]
        GetDllLibPdf().PdfPageLabels_GetPageLabel.restype = c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPdf().PdfPageLabels_GetPageLabel,self.Ptr, index))
        return ret

    @staticmethod
    def Decimal_Arabic_Numerals_Style() -> str:
        """
        Gets the decimal arabic numerals style to be used for the numeric portion of each page label.

        Returns:
            The decimal arabic numerals style.
        """
        GetDllLibPdf().PdfPageLabels_Decimal_Arabic_Numerals_Style.restype = c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPdf().PdfPageLabels_Decimal_Arabic_Numerals_Style))
        return ret

    @staticmethod
    def Uppercase_Roman_Numerals_Style() -> str:
        """
        Gets the uppercase roman numerals style to be used for the numeric portion of each page label.

        Returns:
            The uppercase roman numerals style.
        """
        GetDllLibPdf().PdfPageLabels_Uppercase_Roman_Numerals_Style.restype = c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPdf().PdfPageLabels_Uppercase_Roman_Numerals_Style))
        return ret

    @staticmethod
    def Lowercase_Roman_Numerals_Style() -> str:
        """
        Gets the lowercase roman numerals style to be used for the numeric portion of each page label.

        Returns:
            The lowercase roman numerals style.
        """
        GetDllLibPdf().PdfPageLabels_Lowercase_Roman_Numerals_Style.restype = c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPdf().PdfPageLabels_Lowercase_Roman_Numerals_Style))
        return ret

    @staticmethod
    def Uppercase_Letters_Style() -> str:
        """
        Gets the uppercase letters style to be used for the numeric portion of each page label.

        Returns:
            The uppercase letters style.
        """
        GetDllLibPdf().PdfPageLabels_Uppercase_Letters_Style.restype = c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPdf().PdfPageLabels_Uppercase_Letters_Style))
        return ret

    @staticmethod
    def Lowercase_Letters_Style() -> str:
        """
        Gets the lowercase letters style to be used for the numeric portion of each page label.

        Returns:
            The lowercase letters style.
        """
        GetDllLibPdf().PdfPageLabels_Lowercase_Letters_Style.restype = c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPdf().PdfPageLabels_Lowercase_Letters_Style))
        return ret