from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfSecurity(SpireObject):
    """
    Represents the security settings of the PDF document.
    """

    @property
    def OwnerPassword(self) -> str:
        """
        Gets the owner password.
        """
        GetDllLibPdf().PdfSecurity_get_OwnerPassword.argtypes = [c_void_p]
        GetDllLibPdf().PdfSecurity_get_OwnerPassword.restype = c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPdf().PdfSecurity_get_OwnerPassword,self.Ptr))
        return ret

    @property
    def UserPassword(self) -> str:
        """
        Gets the user password.
        """
        GetDllLibPdf().PdfSecurity_get_UserPassword.argtypes = [c_void_p]
        GetDllLibPdf().PdfSecurity_get_UserPassword.restype = c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPdf().PdfSecurity_get_UserPassword,self.Ptr))
        return ret

    @property
    def OriginalEncrypt(self) -> bool:
        """
        Indicate whether this pdf document was encrypted originally or not. 
        """
        GetDllLibPdf().PdfSecurity_get_OriginalEncrypt.argtypes = [c_void_p]
        GetDllLibPdf().PdfSecurity_get_OriginalEncrypt.restype = c_bool
        ret = CallCFunction(GetDllLibPdf().PdfSecurity_get_OriginalEncrypt,self.Ptr)
        return ret

    @dispatch
    def DecryptUserPassWord(self):
        """
        Decrypt user password
        """
        GetDllLibPdf().PdfSecurity_DecryptUserPassWord.argtypes = [c_void_p]
        CallCFunction(GetDllLibPdf().PdfSecurity_DecryptUserPassWord,self.Ptr)

    @dispatch
    def DecryptUserPassWord(self, ownerPassword: str):
        """
        Decrypt user password.
        Args: ownerPassword: The ownerPassword
        """
        GetDllLibPdf().PdfSecurity_DecryptUserPassWordO.argtypes = [c_void_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfSecurity_DecryptUserPassWordO,self.Ptr, ownerPassword)

    def DecryptOwnerPassWord(self, ownerPassword: str):
        """
        Decrypt all password.
        Args: ownerPassword: The ownerPassword
        """
        GetDllLibPdf().PdfSecurity_DecryptOwnerPassWord.argtypes = [c_void_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfSecurity_DecryptOwnerPassWord,self.Ptr, ownerPassword)

    @dispatch
    def Encrypt(self, openPassword: str):
        """
        To Encrypt the PDF document with open password.
        Note: If set empty string value to open password, it indicates that the PDF document can be operated without providing corresponding password.
        Note: the document owner password should not be exist.
        Args: openPassword: The open password
        """
        GetDllLibPdf().PdfSecurity_Encrypt.argtypes = [c_void_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfSecurity_Encrypt,self.Ptr, openPassword)

    @dispatch
    def Encrypt(self, permissionPassword: str, permissions: PdfPermissionsFlags):
        """
        To Encrypt the PDF document with permission password and permissions.
        Note: The Permission password can't be empty string.
        Args: permissionPassword: The permission password
        Args: permissions: A set of flags specifying which operations are permitted when the document is opened with user access
        """
        enumpermissions: c_int = permissions.value
        GetDllLibPdf().PdfSecurity_EncryptPP.argtypes = [c_void_p, c_wchar_p, c_int]
        CallCFunction(GetDllLibPdf().PdfSecurity_EncryptPP,self.Ptr, permissionPassword, enumpermissions)

    @dispatch
    def Encrypt(self, openPassword: str, permissionPassword: str, permissions: PdfPermissionsFlags, keySize: PdfEncryptionKeySize):
        """
        To Encrypt the PDF document and set the encryption key size and permissions.
        Note: If set empty string value to open password or permission password, it indicates that the PDF document can be operated without providing corresponding password.
        Args: openPassword: The open password
        Args: permissionPassword: The permission password
        Args: permissions: A set of flags specifying which operations are permitted when the document is opened with user access
        Args: keySize: The bit length of the encryption key
        Returns:
        """
        enumpermissions: c_int = permissions.value
        enumkeySize: c_int = keySize.value
        GetDllLibPdf().PdfSecurity_EncryptOPPK.argtypes = [c_void_p, c_wchar_p, c_wchar_p, c_int, c_int]
        CallCFunction(GetDllLibPdf().PdfSecurity_EncryptOPPK,self.Ptr, openPassword, permissionPassword, enumpermissions, enumkeySize)
    @dispatch
    def Encrypt(self, openPassword: str, permissionPassword: str, permissionsInt: int, keySize: PdfEncryptionKeySize):
        """
        To Encrypt the PDF document and set the encryption key size and permissions.
        Note: If set empty string value to open password or permission password, it indicates that the PDF document can be operated without providing corresponding password.
        Args: openPassword: The open password
        Args: permissionPassword: The permission password
        Args: permissions: A set of flags specifying which operations are permitted when the document is opened with user access
        Args: keySize: The bit length of the encryption key
        Returns:
        """
        enumkeySize: c_int = keySize.value
        GetDllLibPdf().PdfSecurity_EncryptOPPK.argtypes = [c_void_p, c_wchar_p, c_wchar_p, c_int, c_int]
        CallCFunction(GetDllLibPdf().PdfSecurity_EncryptOPPK,self.Ptr, openPassword, permissionPassword, permissionsInt, enumkeySize)

    @dispatch
    def Encrypt(self, openPassword: str, permissionPassword: str, permissions: PdfPermissionsFlags, keySize: PdfEncryptionKeySize, originalPermissionPassword: str):
        """
        To Encrypt the PDF document with open password and permission password, and set the encryption key size and permissions.
        Note: If set empty string value to open password or permission password, it indicates that the PDF document can be operated without providing corresponding password.
        Args: openPassword: The open password
        Args: permissionPassword: The permission password
        Args: permissions: A set of flags specifying which operations are permitted when the document is opened with user access
        Args: keySize: The bit length of the encryption key
        Args: originalPermissionPassword: The original permissionPassword of the document
        """
        enumpermissions: c_int = permissions.value
        enumkeySize: c_int = keySize.value
        GetDllLibPdf().PdfSecurity_EncryptOPPKO.argtypes = [c_void_p, c_wchar_p, c_wchar_p, c_int, c_int, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfSecurity_EncryptOPPKO,self.Ptr, openPassword, permissionPassword, enumpermissions, enumkeySize, originalPermissionPassword)

    @property
    def Permissions(self) -> 'PdfPermissionsFlags':
        """
        Gets the document's permission flags
        """
        GetDllLibPdf().PdfSecurity_get_Permissions.argtypes = [c_void_p]
        GetDllLibPdf().PdfSecurity_get_Permissions.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfSecurity_get_Permissions,self.Ptr)
        objwrapped = PdfPermissionsFlags(ret)
        return objwrapped

    @property
    def KeySize(self) -> 'PdfEncryptionKeySize':
        """
        Gets the size of the key.
        """
        GetDllLibPdf().PdfSecurity_get_KeySize.argtypes = [c_void_p]
        GetDllLibPdf().PdfSecurity_get_KeySize.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfSecurity_get_KeySize,self.Ptr)
        objwrapped = PdfEncryptionKeySize(ret)
        return objwrapped