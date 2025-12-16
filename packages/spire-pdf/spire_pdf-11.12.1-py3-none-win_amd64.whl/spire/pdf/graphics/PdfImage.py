from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfImage(PdfShapeWidget):
    """
    Represents the base class for images.
    """

    @property
    def Height(self) -> int:
        """
        Gets the height of the image in pixels.
        """
        GetDllLibPdf().PdfImage_get_Height.argtypes = [c_void_p]
        GetDllLibPdf().PdfImage_get_Height.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfImage_get_Height,self.Ptr)
        return ret

    @property
    def PngDirectToJpeg(self) -> bool:
        """
        If True, png direct convert to Jpx and no mask.
        """
        GetDllLibPdf().PdfImage_get_PngDirectToJpeg.argtypes = [c_void_p]
        GetDllLibPdf().PdfImage_get_PngDirectToJpeg.restype = c_bool
        ret = CallCFunction(GetDllLibPdf().PdfImage_get_PngDirectToJpeg,self.Ptr)
        return ret

    @PngDirectToJpeg.setter
    def PngDirectToJpeg(self, value: bool):
        GetDllLibPdf().PdfImage_set_PngDirectToJpeg.argtypes = [c_void_p, c_bool]
        CallCFunction(GetDllLibPdf().PdfImage_set_PngDirectToJpeg,self.Ptr, value)

    @property
    def Width(self) -> int:
        """
        Gets the width of the image in pixels.
        """
        GetDllLibPdf().PdfImage_get_Width.argtypes = [c_void_p]
        GetDllLibPdf().PdfImage_get_Width.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfImage_get_Width,self.Ptr)
        return ret

    @property
    def HorizontalResolution(self) -> float:
        """
        Gets the horizontal resolution, in pixels per inch, of this Image.
        """
        GetDllLibPdf().PdfImage_get_HorizontalResolution.argtypes = [c_void_p]
        GetDllLibPdf().PdfImage_get_HorizontalResolution.restype = c_float
        ret = CallCFunction(GetDllLibPdf().PdfImage_get_HorizontalResolution,self.Ptr)
        return ret

    @property
    def VerticalResolution(self) -> float:
        """
        Gets the vertical resolution, in pixels per inch, of this Image.
        """
        GetDllLibPdf().PdfImage_get_VerticalResolution.argtypes = [c_void_p]
        GetDllLibPdf().PdfImage_get_VerticalResolution.restype = c_float
        ret = CallCFunction(GetDllLibPdf().PdfImage_get_VerticalResolution,self.Ptr)
        return ret

    @property
    def PhysicalDimension(self) -> 'SizeF':
        """
        Returns the size of the image in points.
        """
        GetDllLibPdf().PdfImage_get_PhysicalDimension.argtypes = [c_void_p]
        GetDllLibPdf().PdfImage_get_PhysicalDimension.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfImage_get_PhysicalDimension,self.Ptr)
        ret = None if intPtr == None else SizeF(intPtr)
        return ret

    @property
    def ActiveFrame(self) -> int:
        """
        Gets or sets the active frame of the image.
        """
        GetDllLibPdf().PdfImage_get_ActiveFrame.argtypes = [c_void_p]
        GetDllLibPdf().PdfImage_get_ActiveFrame.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfImage_get_ActiveFrame,self.Ptr)
        return ret

    @ActiveFrame.setter
    def ActiveFrame(self, value: int):
        GetDllLibPdf().PdfImage_set_ActiveFrame.argtypes = [c_void_p, c_int]
        CallCFunction(GetDllLibPdf().PdfImage_set_ActiveFrame,self.Ptr, value)

    @property
    def FrameCount(self) -> int:
        """
        Gets the number of frames in the image.
        """
        GetDllLibPdf().PdfImage_get_FrameCount.argtypes = [c_void_p]
        GetDllLibPdf().PdfImage_get_FrameCount.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfImage_get_FrameCount,self.Ptr)
        return ret

    @staticmethod
    def FromFile(path: str) -> 'PdfImage':
        """
        Creates PdfImage from a file.
        """
        GetDllLibPdf().PdfImage_FromFile.argtypes = [c_wchar_p]
        GetDllLibPdf().PdfImage_FromFile.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfImage_FromFile,path)
        ret = None if intPtr == None else PdfImage(intPtr)
        return ret

    @staticmethod
    def FromStream(stream: 'Stream') -> 'PdfImage':
        """
        Creates PdfImage from stream.
        """
        intPtrstream: c_void_p = stream.Ptr

        GetDllLibPdf().PdfImage_FromStream.argtypes = [c_void_p]
        GetDllLibPdf().PdfImage_FromStream.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfImage_FromStream,intPtrstream)
        ret = None if intPtr == None else PdfImage(intPtr)
        return ret

    #@staticmethod
    #def FromImage(image: 'Image') -> 'PdfImage':
    #    """
    #    Converts a object into a PDF image.
    #    """
    #    intPtrimage: c_void_p = image.Ptr

    #    GetDllLibPdf().PdfImage_FromImage.argtypes = [c_void_p]
    #    GetDllLibPdf().PdfImage_FromImage.restype = c_void_p
    #    intPtr = CallCFunction(GetDllLibPdf().PdfImage_FromImage,intPtrimage)
    #    ret = None if intPtr == None else PdfImage(intPtr)
    #    return ret

    @staticmethod
    @dispatch
    def FromRtf(rtf: str, width: float, type: PdfImageType, format: PdfStringFormat) -> 'PdfImage':
        """
        Creates a new image instance from RTF text.
        """
        enumtype: c_int = type.value
        intPtrformat: c_void_p = format.Ptr

        GetDllLibPdf().PdfImage_FromRtfRWHTF.argtypes = [c_wchar_p, c_float, c_float, c_int, c_void_p]
        GetDllLibPdf().PdfImage_FromRtfRWHTF.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfImage_FromRtfRWHTF,rtf, width, height, enumtype, intPtrformat)
        ret = None if intPtr == None else PdfImage(intPtr)
        return ret

    @staticmethod
    @dispatch
    def FromRtf(rtf: str, width: float, height: float, type: PdfImageType, format: PdfStringFormat) -> 'PdfImage':
        """
        Creates a new image instance from RTF text.
        """
        enumtype: c_int = type.value
        intPtrformat: c_void_p = format.Ptr

        GetDllLibPdf().PdfImage_FromRtfRWHTF.argtypes = [c_wchar_p, c_float, c_float, c_int, c_void_p]
        GetDllLibPdf().PdfImage_FromRtfRWHTF.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfImage_FromRtfRWHTF,rtf, width, height, enumtype, intPtrformat)
        ret = None if intPtr == None else PdfImage(intPtr)
        return ret