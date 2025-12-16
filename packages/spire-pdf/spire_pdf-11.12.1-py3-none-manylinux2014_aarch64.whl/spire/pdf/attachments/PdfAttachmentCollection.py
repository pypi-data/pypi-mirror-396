from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfAttachmentCollection(PdfCollection):
    """
    Represents a collection of attachment objects.
    """

    def get_Item(self, index: int) -> 'PdfAttachment':
        """
        Gets attachment by its index in the collection.
        Args: index: Index of the attachment.
        Returns: Attachment object by its index in the collection.
        """
        GetDllLibPdf().PdfAttachmentCollection_get_Item.argtypes = [c_void_p, c_int]
        GetDllLibPdf().PdfAttachmentCollection_get_Item.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfAttachmentCollection_get_Item,self.Ptr, index)
        ret = None if intPtr == None else PdfAttachment(intPtr)
        return ret

    @dispatch
    def Add(self, attachment: PdfAttachment) -> int:
        """
        Adds the specified attachment.
        Args: attachment: The attachment.
        Returns: Position of the inserted attachment.
        """
        intPtrattachment: c_void_p = attachment.Ptr
        GetDllLibPdf().PdfAttachmentCollection_Add.argtypes = [c_void_p, c_void_p]
        GetDllLibPdf().PdfAttachmentCollection_Add.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfAttachmentCollection_Add,self.Ptr, intPtrattachment)
        return ret

    @dispatch
    def Add(self, attachment: PdfAttachment, associatedDocument, association: PdfAttachmentRelationship) -> int:
        """
        Adds the specified attachment.
        Args: attachment: The attachment.
        Args: associatedDocument: The associated document.
        Args: association: The relationship between attachment and associated document.
        Returns: Position of the inserted attachment.
        """
        intPtrattachment: c_void_p = attachment.Ptr
        intPtrassociatedDocument: c_void_p = associatedDocument.Ptr
        enumassociation: c_int = association.value
        GetDllLibPdf().PdfAttachmentCollection_AddAAA.argtypes = [c_void_p, c_void_p, c_void_p, c_int]
        GetDllLibPdf().PdfAttachmentCollection_AddAAA.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfAttachmentCollection_AddAAA,self.Ptr, intPtrattachment, intPtrassociatedDocument, enumassociation)
        return ret

    def Insert(self, index: int, attachment: 'PdfAttachment'):
        """
        Inserts the specified index.
        Args: index: The index.
        Args: attachment: The attachment.
        """
        intPtrattachment: c_void_p = attachment.Ptr
        GetDllLibPdf().PdfAttachmentCollection_Insert.argtypes = [c_void_p, c_int, c_void_p]
        CallCFunction(GetDllLibPdf().PdfAttachmentCollection_Insert,self.Ptr, index, intPtrattachment)

    def Remove(self, attachment: 'PdfAttachment'):
        """
        Removes the specified attachment.
        Args: attachment: The attachment.
        """
        intPtrattachment: c_void_p = attachment.Ptr
        GetDllLibPdf().PdfAttachmentCollection_Remove.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfAttachmentCollection_Remove,self.Ptr, intPtrattachment)

    def RemoveAt(self, index: int):
        """
        Removes attachment at the specified index.
        Args: index: The index.
        """
        GetDllLibPdf().PdfAttachmentCollection_RemoveAt.argtypes = [c_void_p, c_int]
        CallCFunction(GetDllLibPdf().PdfAttachmentCollection_RemoveAt,self.Ptr, index)

    def IndexOf(self, attachment: 'PdfAttachment') -> int:
        """
        Indexes the of attachment.
        Args: attachment: The attachment.
        Returns: Index of the attachment.
        """
        intPtrattachment: c_void_p = attachment.Ptr
        GetDllLibPdf().PdfAttachmentCollection_IndexOf.argtypes = [c_void_p, c_void_p]
        GetDllLibPdf().PdfAttachmentCollection_IndexOf.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfAttachmentCollection_IndexOf,self.Ptr, intPtrattachment)
        return ret

    def Contains(self, attachment: 'PdfAttachment') -> bool:
        """
        Determines whether the collection contains the specified attachment.
        Args: attachment: The attachment.
        Returns: True if it contains the specified attachment, False otherwise.
        """
        intPtrattachment: c_void_p = attachment.Ptr
        GetDllLibPdf().PdfAttachmentCollection_Contains.argtypes = [c_void_p, c_void_p]
        GetDllLibPdf().PdfAttachmentCollection_Contains.restype = c_bool
        ret = CallCFunction(GetDllLibPdf().PdfAttachmentCollection_Contains,self.Ptr, intPtrattachment)
        return ret

    def Clear(self):
        """
        Clears the collection.
        """
        GetDllLibPdf().PdfAttachmentCollection_Clear.argtypes = [c_void_p]
        CallCFunction(GetDllLibPdf().PdfAttachmentCollection_Clear,self.Ptr)