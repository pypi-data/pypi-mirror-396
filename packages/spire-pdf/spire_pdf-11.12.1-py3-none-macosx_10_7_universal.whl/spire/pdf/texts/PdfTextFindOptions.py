from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfTextFindOptions(SpireObject):
    """
    Represents text search options
    """
    @dispatch
    def __init__(self):
        GetDllLibPdf().PdfTextFindOptions_CreatePdfTextFindOptions.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfTextFindOptions_CreatePdfTextFindOptions)
        super(PdfTextFindOptions, self).__init__(intPtr)

    @property
    def Area(self) -> 'RectangleF':
        """
        Gets or sets the search area.
        """
        return None

    @Area.setter
    def Area(self, value: 'RectangleF'):
        """
        Sets the search area.
        """
        GetDllLibPdf().PdfTextFindOptions_set_Area.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfTextFindOptions_set_Area,self.Ptr, value.Ptr)

    @property
    def IsShowHiddenText(self) -> bool:
        """
        Gets or sets whether to show hidden texts.
        Default value: False.
        """
        GetDllLibPdf().PdfTextFindOptions_get_IsShowHiddenText.argtypes = [c_void_p]
        GetDllLibPdf().PdfTextFindOptions_get_IsShowHiddenText.restype = c_bool
        ret = CallCFunction(GetDllLibPdf().PdfTextFindOptions_get_IsShowHiddenText,self.Ptr)
        return ret

    @IsShowHiddenText.setter
    def IsShowHiddenText(self, value: bool):
        """
        Sets whether to show hidden texts.
        """
        GetDllLibPdf().PdfTextFindOptions_set_IsShowHiddenText.argtypes = [c_void_p, c_bool]
        CallCFunction(GetDllLibPdf().PdfTextFindOptions_set_IsShowHiddenText,self.Ptr, value)

    @property
    def Parameter(self) -> 'TextFindParameter':
        """
        Gets or sets the text find parameter.
        Default value: TextFindParameter.None.
        """
        GetDllLibPdf().PdfTextFindOptions_get_Parameter.argtypes = [c_void_p]
        GetDllLibPdf().PdfTextFindOptions_get_Parameter.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfTextFindOptions_get_Parameter,self.Ptr)
        objwrapped = TextFindParameter(ret)
        return objwrapped

    @Parameter.setter
    def Parameter(self, value: 'TextFindParameter'):
        """
        Sets the text find parameter.
        """
        GetDllLibPdf().PdfTextFindOptions_set_Parameter.argtypes = [c_void_p, c_int]
        CallCFunction(GetDllLibPdf().PdfTextFindOptions_set_Parameter,self.Ptr, value.value)