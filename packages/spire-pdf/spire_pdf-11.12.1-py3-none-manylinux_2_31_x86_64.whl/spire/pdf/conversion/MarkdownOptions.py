from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class MarkdownOptions(SpireObject):
    @dispatch
    def __init__(self):
        """
        Represent pdf to MarkdownOptions
        """
        GetDllLibPdf().MarkdownOptions_CreateMarkdownOptions.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().MarkdownOptions_CreateMarkdownOptions)
        super(MarkdownOptions, self).__init__(intPtr)   

    @property
    def IgnoreImage(self) -> bool:
        """
        whether to convert the image in pdf to markdown.
        """
        GetDllLibPdf().MarkdownOptions_get_IgnoreImage.argtypes = [c_void_p]
        GetDllLibPdf().MarkdownOptions_get_IgnoreImage.restype = c_bool
        ret = CallCFunction(GetDllLibPdf().MarkdownOptions_get_IgnoreImage,self.Ptr)
        return ret

    @IgnoreImage.setter
    def IgnoreImage(self, value: bool):
        """
        whether to convert the image in pdf to markdown.
        """
        GetDllLibPdf().MarkdownOptions_set_IgnoreImage.argtypes = [c_void_p, c_bool]
        CallCFunction(GetDllLibPdf().MarkdownOptions_set_IgnoreImage,self.Ptr, value)


