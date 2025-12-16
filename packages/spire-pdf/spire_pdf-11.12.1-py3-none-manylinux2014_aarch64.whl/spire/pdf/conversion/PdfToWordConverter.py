from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfToWordConverter(SpireObject):
    """
    This class provides support for converting a pdf document to a word document.
    """
    @dispatch
    def __init__(self, filePath: str):
        """
        Initializes a new instance of the PdfToWordConverter class with the specified file path.

        Args:
            filePath (str): The path of the PDF file.
        """
        GetDllLibPdf().PdfToWordConverter_CreatePdfToWordConverterF.argtypes = [c_wchar_p]
        GetDllLibPdf().PdfToWordConverter_CreatePdfToWordConverterF.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfToWordConverter_CreatePdfToWordConverterF,filePath)
        super(PdfToWordConverter, self).__init__(intPtr)

    @dispatch
    def __init__(self, filePath: str, password:str):
        """
        Initializes a new instance of the PdfToWordConverter class with the specified file path and file password.

        Args:
            filePath (str): The path of the PDF file.
            password (str): The pdf document password.
        """
        GetDllLibPdf().PdfToWordConverter_CreatePdfToWordConverterFP.argtypes = [c_wchar_p,c_wchar_p]
        GetDllLibPdf().PdfToWordConverter_CreatePdfToWordConverterFP.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfToWordConverter_CreatePdfToWordConverterFP,filePath,password)
        super(PdfToWordConverter, self).__init__(intPtr)

    @dispatch
    def __init__(self, stream: Stream):
        """
        Initializes a new instance of the PdfToWordConverter class with the specified stream.

        Args:
            stream (Stream): The stream containing the PDF data.
        """
        ptrStream: c_void_p = stream.Ptr
        GetDllLibPdf().PdfToWordConverter_CreatePdfToWordConverterS.argtypes = [c_void_p]
        GetDllLibPdf().PdfToWordConverter_CreatePdfToWordConverterS.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfToWordConverter_CreatePdfToWordConverterS,ptrStream)
        super(PdfToWordConverter, self).__init__(intPtr)

    @property
    def ConvertOptions(self) -> 'PdfConvertOptions':
        """
        Gets Parameters for the converter.

        Returns:
            ConvertOptions: Parameters for the converter.
        """
        GetDllLibPdf().PdfToWordConverter_get_ConvertOptions.argtypes = [c_void_p]
        GetDllLibPdf().PdfToWordConverter_get_ConvertOptions.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfToWordConverter_get_ConvertOptions,self.Ptr)
        ret = None if intPtr == None else PdfConvertOptions(intPtr)
        return ret

    @dispatch
    def SaveToDocx(self, fileStream: Stream):
        """
        Convert to word document,the extension is docx

        Args:
            fileStream (Stream): The output file stream.
        """
        intPtrfileStream: c_void_p = fileStream.Ptr

        GetDllLibPdf().PdfToWordConverter_SaveToDocx.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfToWordConverter_SaveToDocx,self.Ptr, intPtrfileStream)

    @dispatch
    def SaveToDocx(self, filename: str):
        """
        Convert to word document,the extension is docx

        Args:
            filename (str): The output file name.
        """
        GetDllLibPdf().PdfToWordConverter_SaveToDocxF.argtypes = [c_void_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfToWordConverter_SaveToDocxF,self.Ptr, filename)

