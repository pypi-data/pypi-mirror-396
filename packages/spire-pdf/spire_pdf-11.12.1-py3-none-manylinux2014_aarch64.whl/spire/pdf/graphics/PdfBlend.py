from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfBlend(PdfBlendBase):
    """
    Implements blend brush setting and functions.
    """

    @property
    def Factors(self) -> List[float]:
        """
        Gets or sets the factors array.
        """
        GetDllLibPdf().PdfBlend_get_Factors.argtypes = [c_void_p]
        GetDllLibPdf().PdfBlend_get_Factors.restype = IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPdf().PdfBlend_get_Factors,self.Ptr)
        ret = GetVectorFromArray(intPtrArray, c_float)
        return ret

    @Factors.setter
    def Factors(self, value: List[float]):
        """
        Sets the factors array.
        """
        vCount = len(value)
        ArrayType = c_float * vCount
        vArray = ArrayType()
        for i in range(0, vCount):
            vArray[i] = value[i]
        GetDllLibPdf().PdfBlend_set_Factors.argtypes = [c_void_p, ArrayType, c_int]
        CallCFunction(GetDllLibPdf().PdfBlend_set_Factors,self.Ptr, vArray, vCount)