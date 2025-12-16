from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple,overload
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfPasswordSecurityPolicy(PdfSecurityPolicy):
    """Represents the password security policy of the PDF document.

    """
    @dispatch
    def __init__(self, userPassword:str, ownerPassword:str):
        GetDllLibPdf().PdfPasswordSecurityPolicy_CreatePdfPasswordSecurityPolicyUO.argtypes=[c_wchar_p,c_wchar_p]
        GetDllLibPdf().PdfPasswordSecurityPolicy_CreatePdfPasswordSecurityPolicyUO.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPasswordSecurityPolicy_CreatePdfPasswordSecurityPolicyUO,userPassword,ownerPassword)
        super(PdfPasswordSecurityPolicy, self).__init__(intPtr)




