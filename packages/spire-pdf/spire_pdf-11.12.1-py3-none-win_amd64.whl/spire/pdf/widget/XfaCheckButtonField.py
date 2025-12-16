from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class XfaCheckButtonField(XfaField):
    """
    Represents a check button field in an XFA form.
    """

    @property
    def Checked(self) -> bool:
        """
        Gets or sets a value indicating whether the check button field is checked.
        """
        GetDllLibPdf().XfaCheckButtonField_get_Checked.argtypes = [c_void_p]
        GetDllLibPdf().XfaCheckButtonField_get_Checked.restype = c_bool
        ret = CallCFunction(GetDllLibPdf().XfaCheckButtonField_get_Checked,self.Ptr)
        return ret

    @Checked.setter
    def Checked(self, value: bool):
        """
        Sets a value indicating whether the check button field is checked.
        """
        GetDllLibPdf().XfaCheckButtonField_set_Checked.argtypes = [c_void_p, c_bool]
        CallCFunction(GetDllLibPdf().XfaCheckButtonField_set_Checked,self.Ptr, value)