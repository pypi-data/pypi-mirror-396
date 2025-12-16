from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfPKCS7Formatter(IPdfSignatureFormatter, Security_IPdfSignatureFormatter):
    """
    Pdf pkcs7 signature implementation.
    """

    @property
    def Properties(self) -> 'PdfSignatureProperties':
        """
        The signature properties.
        """
        GetDllLibPdf().PdfPKCS7Formatter_get_Properties.argtypes = [c_void_p]
        GetDllLibPdf().PdfPKCS7Formatter_get_Properties.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPKCS7Formatter_get_Properties,self.Ptr)
        ret = None if intPtr == None else PdfSignatureProperties(intPtr)
        return ret

    @property
    def OCSPService(self) -> 'IOCSPService':
        """
        The service which generate OCSP response.
        """
        GetDllLibPdf().PdfPKCS7Formatter_get_OCSPService.argtypes = [c_void_p]
        GetDllLibPdf().PdfPKCS7Formatter_get_OCSPService.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPKCS7Formatter_get_OCSPService,self.Ptr)
        ret = None if intPtr == None else IOCSPService(intPtr)
        return ret

    @OCSPService.setter
    def OCSPService(self, value: 'IOCSPService'):
        GetDllLibPdf().PdfPKCS7Formatter_set_OCSPService.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfPKCS7Formatter_set_OCSPService,self.Ptr, value.Ptr)

    @property
    def TimestampService(self) -> 'ITSAService':
        """
        The provider which generate timestamp token.
        """
        GetDllLibPdf().PdfPKCS7Formatter_get_TimestampService.argtypes = [c_void_p]
        GetDllLibPdf().PdfPKCS7Formatter_get_TimestampService.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPKCS7Formatter_get_TimestampService,self.Ptr)
        ret = None if intPtr == None else ITSAService(intPtr)
        return ret

    @TimestampService.setter
    def TimestampService(self, value: 'ITSAService'):
        GetDllLibPdf().PdfPKCS7Formatter_set_TimestampService.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfPKCS7Formatter_set_TimestampService,self.Ptr, value.Ptr)