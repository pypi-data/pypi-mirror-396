from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class XfaTextField(XfaField):
    """
    Represents a text field in an XFA form.
    """

    @property
    def Value(self) -> str:
        """
        Gets the value of the text field.
        """
        GetDllLibPdf().XfaTextField_get_Value.argtypes = [c_void_p]
        GetDllLibPdf().XfaTextField_get_Value.restype = c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPdf().XfaTextField_get_Value,self.Ptr))
        return ret

    @Value.setter
    def Value(self, value: str):
        """
        Sets the value of the text field.
        """
        GetDllLibPdf().XfaTextField_set_Value.argtypes = [c_void_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().XfaTextField_set_Value,self.Ptr, value)