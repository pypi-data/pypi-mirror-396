from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfWatermarkAnnotation(PdfAnnotation):
    """
    The water mark annotation.
    """
    @dispatch
    def __init__(self, rectangle: RectangleF, text: str):
        """
        Initializes a new instance of the  class.

        Args:
            rectangle: RectangleF structure that specifies the bounds of the annotation.
            text: Text of the fixed print annotation..
        """
        ptrRec: c_void_p = rectangle.Ptr
        GetDllLibPdf().PdfWatermarkAnnotation_CreatePdfWatermarkAnnotationRT.argtypes = [c_void_p, c_wchar_p]
        GetDllLibPdf().PdfWatermarkAnnotation_CreatePdfWatermarkAnnotationRT.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfWatermarkAnnotation_CreatePdfWatermarkAnnotationRT,ptrRec, text)
        super(PdfWatermarkAnnotation, self).__init__(intPtr)

    @dispatch
    def __init__(self, rectangle: RectangleF):
        """
        Initializes a new instance of the  class.

        Args:
            rectangle: RectangleF structure that specifies the bounds of the annotation.
        """
        ptrRec: c_void_p = rectangle.Ptr
        GetDllLibPdf().PdfWatermarkAnnotation_CreatePdfWatermarkAnnotationR.argtypes = [c_void_p]
        GetDllLibPdf().PdfWatermarkAnnotation_CreatePdfWatermarkAnnotationR.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfWatermarkAnnotation_CreatePdfWatermarkAnnotationR,ptrRec)
        super(PdfWatermarkAnnotation, self).__init__(intPtr)

    @property
    def Appearance(self) -> 'PdfAppearance':
        """
        Get the appearance.
        """
        return None

    @Appearance.setter
    def Appearance(self, value: 'PdfAppearance'):
        """
        Set the appearance.
        Args:
            value: The appearance
        """
        GetDllLibPdf().PdfWatermarkAnnotation_set_Appearance.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfWatermarkAnnotation_set_Appearance,self.Ptr, value.Ptr)

    def SetMatrix(self, matrix: List[float]):
        """
        Set the matrix.
        Args:
            matrix: The matrix.
        """
        countmatrix = len(matrix)
        ArrayTypematrix = c_float * countmatrix
        arraymatrix = ArrayTypematrix()
        for i in range(0, countmatrix):
            arraymatrix[i] = matrix[i]

        GetDllLibPdf().PdfWatermarkAnnotation_SetMatrix.argtypes = [c_void_p, ArrayTypematrix]
        CallCFunction(GetDllLibPdf().PdfWatermarkAnnotation_SetMatrix,self.Ptr, arraymatrix,countmatrix)

    def SetHorizontalTranslation(self, horizontal: float):
        """
        Set the horizontal translation.
        Args:
            horizontal: The horizontal.
        """
        GetDllLibPdf().PdfWatermarkAnnotation_SetHorizontalTranslation.argtypes = [c_void_p, c_float]
        CallCFunction(GetDllLibPdf().PdfWatermarkAnnotation_SetHorizontalTranslation,self.Ptr, horizontal)

    def SetVerticalTranslation(self, vertical: float):
        """
        Set the vertical translation.
        Args:
            vertical: The vertical.
        """
        GetDllLibPdf().PdfWatermarkAnnotation_SetVerticalTranslation.argtypes = [c_void_p, c_float]
        CallCFunction(GetDllLibPdf().PdfWatermarkAnnotation_SetVerticalTranslation,self.Ptr, vertical)