from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfTextReplaceOptions(SpireObject):
    """
    the replace options.
    """
    @dispatch
    def __init__(self):
        GetDllLibPdf().PdfTextReplaceOptions_CreatePdfTextReplaceOptions.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfTextReplaceOptions_CreatePdfTextReplaceOptions)
        super(PdfTextReplaceOptions, self).__init__(intPtr)

    @property
    def ReplaceType(self) -> 'ReplaceActionType':
        """
        Gets or sets replace action type. Default value : ReplaceActionType.None
        """
        GetDllLibPdf().PdfTextReplaceOptions_get_ReplaceType.argtypes = [c_void_p]
        GetDllLibPdf().PdfTextReplaceOptions_get_ReplaceType.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfTextReplaceOptions_get_ReplaceType,self.Ptr)
        objwrapped = ReplaceActionType(ret)
        return objwrapped

    @ReplaceType.setter
    def ReplaceType(self, value: 'ReplaceActionType'):
        """
        Sets the replace action type.
        """
        GetDllLibPdf().PdfTextReplaceOptions_set_ReplaceType.argtypes = [c_void_p, c_int]
        CallCFunction(GetDllLibPdf().PdfTextReplaceOptions_set_ReplaceType,self.Ptr, value.value)

