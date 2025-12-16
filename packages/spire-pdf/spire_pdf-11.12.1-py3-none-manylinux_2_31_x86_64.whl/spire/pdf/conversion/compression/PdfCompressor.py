from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfCompressor(SpireObject):
    """
    The pdf document compressor.
    """
    @dispatch
    def __init__(self, filePath: str):
        """
        Construct a new converter.

        Args:
            filePath (str): The path of the PDF file.
        """
        GetDllLibPdf().PdfCompressor_CreatePdfCompressorF.argtypes = [c_wchar_p]
        GetDllLibPdf().PdfCompressor_CreatePdfCompressorF.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfCompressor_CreatePdfCompressorF,filePath)
        super(PdfCompressor, self).__init__(intPtr)

    @dispatch
    def __init__(self, stream: Stream):
        """
         Initializes a new instance of the class.

        Args:
            stream (Stream): The stream containing the PDF data.
        """
        ptrStream: c_void_p = stream.Ptr
        GetDllLibPdf().PdfCompressor_CreatePdfCompressorS.argtypes = [c_void_p]
        GetDllLibPdf().PdfCompressor_CreatePdfCompressorS.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfCompressor_CreatePdfCompressorS,ptrStream)
        super(PdfCompressor, self).__init__(intPtr)

    @dispatch
    def CompressToStream(self, fileStream: Stream):
        """
        Compress the document to the specified stream.

        Args:
            fileStream (Stream): The output file stream.
        """
        intPtrfileStream: c_void_p = fileStream.Ptr

        GetDllLibPdf().PdfCompressor_CompressToFileS.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfCompressor_CompressToFileS,self.Ptr, intPtrfileStream)

    @dispatch
    def CompressToFile(self, filename: str):
        """
        Compress document.

        Args:
            filename (str): The output file name.
        """
        GetDllLibPdf().PdfCompressor_CompressToFileF.argtypes = [c_void_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfCompressor_CompressToFileF,self.Ptr, filename)

    @property
    def OptimizationOptions(self)->OptimizationOptions:
        """
        The compression options.
        """
        GetDllLibPdf().PdfCompressor_get_OptimizationOptions.argtypes=[c_void_p]
        GetDllLibPdf().PdfCompressor_get_OptimizationOptions.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfCompressor_get_OptimizationOptions,self.Ptr)
        ret = None if intPtr==None else OptimizationOptions(intPtr)
        return ret


    @OptimizationOptions.setter
    def OptimizationOptions(self, value:OptimizationOptions):
        GetDllLibPdf().PdfCompressor_set_OptimizationOptions.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfCompressor_set_OptimizationOptions,self.Ptr, value.Ptr)