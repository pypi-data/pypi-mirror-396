from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfBlendBase(SpireObject):
    """
    Represents the base class for PdfBlend and PdfColorBlend classes.
    Implements basic routines needed by both classes.
    """

    @property
    def Positions(self) -> List[float]:
        """
        Gets or sets the positions array.
        """
        GetDllLibPdf().PdfBlendBase_get_Positions.argtypes = [c_void_p]
        GetDllLibPdf().PdfBlendBase_get_Positions.restype = IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPdf().PdfBlendBase_get_Positions,self.Ptr)
        ret = GetVectorFromArray(intPtrArray, c_float)
        return ret

    @Positions.setter
    def Positions(self, value: List[float]):
        """
        Sets the positions array.
        """
        vCount = len(value)
        ArrayType = c_float * vCount
        vArray = ArrayType()
        for i in range(0, vCount):
            vArray[i] = value[i]
        GetDllLibPdf().PdfBlendBase_set_Positions.argtypes = [c_void_p, ArrayType, c_int]
        CallCFunction(GetDllLibPdf().PdfBlendBase_set_Positions,self.Ptr, vArray, vCount)