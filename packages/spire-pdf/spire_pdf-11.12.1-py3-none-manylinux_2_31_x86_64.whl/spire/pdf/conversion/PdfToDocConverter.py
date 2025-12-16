from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfToDocConverter(SpireObject):
    """
    This class provides support for converting PDF into an XPS Document.
    """

    @dispatch
    def __init__(self):
        """
        Initializes a new instance of the PdfToDocConverter class.
        """
        GetDllLibPdf().PdfToDocConverter_CreatePdfToDocConverter.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfToDocConverter_CreatePdfToDocConverter)
        super(PdfToDocConverter, self).__init__(intPtr)

    @dispatch
    def __init__(self, filePath: str):
        """
        Initializes a new instance of the PdfToDocConverter class with the specified file path.

        Args:
            filePath (str): The path of the PDF file.
        """
        GetDllLibPdf().PdfToDocConverter_CreatePdfToDocConverterF.argtypes = [c_wchar_p]
        GetDllLibPdf().PdfToDocConverter_CreatePdfToDocConverterF.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfToDocConverter_CreatePdfToDocConverterF,filePath)
        super(PdfToDocConverter, self).__init__(intPtr)

    @dispatch
    def __init__(self, stream: Stream):
        """
        Initializes a new instance of the PdfToDocConverter class with the specified stream.

        Args:
            stream (Stream): The stream containing the PDF data.
        """
        ptrStream: c_void_p = stream.Ptr
        GetDllLibPdf().PdfToDocConverter_CreatePdfToDocConverterS.argtypes = [c_void_p]
        GetDllLibPdf().PdfToDocConverter_CreatePdfToDocConverterS.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfToDocConverter_CreatePdfToDocConverterS,ptrStream)
        super(PdfToDocConverter, self).__init__(intPtr)

    @property
    def DocxOptions(self) -> 'DocxOptions':
        """
        Gets or sets the options for converting to DOCX format.

        Returns:
            DocxOptions: The options for converting to DOCX format.
        """
        GetDllLibPdf().PdfToDocConverter_get_DocxOptions.argtypes = [c_void_p]
        GetDllLibPdf().PdfToDocConverter_get_DocxOptions.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfToDocConverter_get_DocxOptions,self.Ptr)
        ret = None if intPtr == None else DocxOptions(intPtr)
        return ret

    @DocxOptions.setter
    def DocxOptions(self, value: 'DocxOptions'):
        """
        Sets the options for converting to DOCX format.

        Args:
            value (DocxOptions): The options for converting to DOCX format.
        """
        GetDllLibPdf().PdfToDocConverter_set_DocxOptions.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfToDocConverter_set_DocxOptions,self.Ptr, value.Ptr)

    @dispatch
    def SaveToDocx(self, fileStream: Stream):
        """
        Converts the PDF to a DOCX document and saves it to the specified file stream.

        Args:
            fileStream (Stream): The output file stream.
        """
        intPtrfileStream: c_void_p = fileStream.Ptr

        GetDllLibPdf().PdfToDocConverter_SaveToDocx.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfToDocConverter_SaveToDocx,self.Ptr, intPtrfileStream)

    @dispatch
    def SaveToDocx(self, fileStream: Stream, isDocx: bool):
        """
        Converts the PDF to a DOCX document and saves it to the specified file stream.

        Args:
            fileStream (Stream): The output file stream.
            isDocx (bool): Indicates whether the output format is DOCX or DOC.
        """
        intPtrfileStream: c_void_p = fileStream.Ptr

        GetDllLibPdf().PdfToDocConverter_SaveToDocxFI.argtypes = [c_void_p, c_void_p, c_bool]
        CallCFunction(GetDllLibPdf().PdfToDocConverter_SaveToDocxFI,self.Ptr, intPtrfileStream, isDocx)

    @dispatch
    def SaveToDocx(self, filename: str):
        """
        Converts the PDF to a DOCX document and saves it to the specified file name.

        Args:
            filename (str): The output file name.
        """
        GetDllLibPdf().PdfToDocConverter_SaveToDocxF.argtypes = [c_void_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfToDocConverter_SaveToDocxF,self.Ptr, filename)

    @dispatch
    def SaveToDocx(self, filename: str, isDocx: bool):
        """
        Converts the PDF to a DOCX document and saves it to the specified file name.

        Args:
            filename (str): The output file name.
            isDocx (bool): Indicates whether the output format is DOCX or DOC.
        """
        GetDllLibPdf().PdfToDocConverter_SaveToDocxFI1.argtypes = [c_void_p, c_wchar_p, c_bool]
        CallCFunction(GetDllLibPdf().PdfToDocConverter_SaveToDocxFI1,self.Ptr, filename, isDocx)