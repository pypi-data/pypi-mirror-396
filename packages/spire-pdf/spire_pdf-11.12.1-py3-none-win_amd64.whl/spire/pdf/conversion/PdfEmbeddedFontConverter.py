from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfEmbeddedFontConverter(SpireObject):
    """
    Construct a new converter.
    """
    @dispatch
    def __init__(self, filePath: str):
        """
        The embedded font conveter. 

        Args:
            filePath (str): The path of the PDF file.
        """
        GetDllLibPdf().PdfEmbeddedFontConverter_CreatePdfEmbeddedFontConverterF.argtypes = [c_wchar_p]
        GetDllLibPdf().PdfEmbeddedFontConverter_CreatePdfEmbeddedFontConverterF.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfEmbeddedFontConverter_CreatePdfEmbeddedFontConverterF,filePath)
        super(PdfEmbeddedFontConverter, self).__init__(intPtr)

    @dispatch
    def __init__(self, stream: Stream):
        """
        Initializes a new instance of the PdfEmbeddedFontConverter class with the specified stream.

        Args:
            stream (Stream): The stream containing the PDF data.
        """
        ptrStream: c_void_p = stream.Ptr
        GetDllLibPdf().PdfEmbeddedFontConverter_CreatePdfEmbeddedFontConverterS.argtypes = [c_void_p]
        GetDllLibPdf().PdfEmbeddedFontConverter_CreatePdfEmbeddedFontConverterS.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfEmbeddedFontConverter_CreatePdfEmbeddedFontConverterS,ptrStream)
        super(PdfEmbeddedFontConverter, self).__init__(intPtr)

    @dispatch
    def ToEmbeddedFontDocument(self, fileStream: Stream):
        """
        Convert to document

        Args:
            fileStream (Stream): The output file stream.
        """
        intPtrfileStream: c_void_p = fileStream.Ptr

        GetDllLibPdf().PdfEmbeddedFontConverter_ToEmbeddedFontDocumentS.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfEmbeddedFontConverter_ToEmbeddedFontDocumentS,self.Ptr, intPtrfileStream)

    @dispatch
    def ToEmbeddedFontDocument(self, filename: str):
        """
        Convert to document

        Args:
            filename (str): The output file name.
        """
        GetDllLibPdf().PdfEmbeddedFontConverter_ToEmbeddedFontDocumentF.argtypes = [c_void_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfEmbeddedFontConverter_ToEmbeddedFontDocumentF,self.Ptr, filename)


