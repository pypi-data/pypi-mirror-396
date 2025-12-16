from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfGrayConverter (SpireObject) :
    """
    The gray pdf conveter.
    """
    @dispatch
    def __init__(self, filePath:str):
        GetDllLibPdf().PdfGrayConverter_CreatePdfGrayConverterF.argtypes=[c_wchar_p]
        GetDllLibPdf().PdfGrayConverter_CreatePdfGrayConverterF.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfGrayConverter_CreatePdfGrayConverterF,filePath)
        super(PdfGrayConverter, self).__init__(intPtr)

    @dispatch
    def __init__(self, stream:Stream):
        ptrStream:c_void_p = stream.Ptr
        GetDllLibPdf().PdfGrayConverter_CreatePdfGrayConverterS.argtypes=[c_void_p]
        GetDllLibPdf().PdfGrayConverter_CreatePdfGrayConverterS.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfGrayConverter_CreatePdfGrayConverterS,ptrStream)
        super(PdfGrayConverter, self).__init__(intPtr)

    @dispatch

    def ToGrayPdf(self ,filePath:str):
        """
        Convert to gray pdf document.

        Args:
            filePath: The out file path.
        """
        GetDllLibPdf().PdfGrayConverter_ToGrayPdf.argtypes=[c_void_p ,c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfGrayConverter_ToGrayPdf,self.Ptr, filePath)

    @dispatch

    def ToGrayPdf(self ,stream:Stream):
        """
        Convert to gray pdf document.

        Args:
            stream: The out stream.
        """
        intPtrstream:c_void_p = stream.Ptr

        GetDllLibPdf().PdfGrayConverter_ToGrayPdfS.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPdf().PdfGrayConverter_ToGrayPdfS,self.Ptr, intPtrstream)

    def Dispose(self):
        """

        """
        GetDllLibPdf().PdfGrayConverter_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibPdf().PdfGrayConverter_Dispose,self.Ptr)

