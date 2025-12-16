from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.ocr.common import *
from spire.ocr import *
from ctypes import *
import abc

class ConfigureOptions(SpireObject):

    @dispatch
    def __init__(self):
        """
        Configure the ocr dependencies options.
        """
        GetDllLibOcr().ConfigureOptions_Create.restype = c_void_p
        intPtr = CallCFunction(GetDllLibOcr().ConfigureOptions_Create)
        super(ConfigureOptions, self).__init__(intPtr)
    @dispatch
    def __init__(self, modelPath:str, language:str):
        """
        Configure the ocr dependencies options.
        Params
            modelPath : the ocr model path
            language : the ocr language(Chinese,English,Chinesetraditional,German,French,Japan,Korean)
        """
        GetDllLibOcr().ConfigureOptions_CreateML.argtypes=[c_wchar_p,c_wchar_p]
        GetDllLibOcr().ConfigureOptions_CreateML.restype = c_void_p
        intPtr = CallCFunction(GetDllLibOcr().ConfigureOptions_CreateML,modelPath,language)
        super(ConfigureOptions, self).__init__(intPtr)

    @property
    def ModelPath(self) -> str:
        """
        Get the ModelPath of the Ocr ConfigureOptions.
        """
        GetDllLibOcr().ConfigureOptions_get_ModelPath.argtypes = [c_void_p]
        GetDllLibOcr().ConfigureOptions_get_ModelPath.restype = c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibOcr().ConfigureOptions_get_ModelPath,self.Ptr))
        return ret

    @ModelPath.setter
    def ModelPath(self, value: str):
        """
        Set the ModelPath of the Ocr ConfigureOptions.
        """
        GetDllLibOcr().ConfigureOptions_set_ModelPath.argtypes = [c_void_p, c_wchar_p]
        CallCFunction(GetDllLibOcr().ConfigureOptions_set_ModelPath,self.Ptr, value)


    @property
    def Language(self) -> str:
        """
        Get the Language of the Ocr ConfigureOptions.
        """
        GetDllLibOcr().ConfigureOptions_get_Language.argtypes = [c_void_p]
        GetDllLibOcr().ConfigureOptions_get_Language.restype = c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibOcr().ConfigureOptions_get_Language,self.Ptr))
        return ret

    @Language.setter
    def Language(self, value: str):
        """
        Set the Language of the Ocr ConfigureOptions.
        """
        GetDllLibOcr().ConfigureOptions_set_Language.argtypes = [c_void_p, c_wchar_p]
        CallCFunction(GetDllLibOcr().ConfigureOptions_set_Language,self.Ptr, value)

    @property
    def AutoRotate(self) -> bool:
        """
        Get the automatic image rotation of the Ocr ConfigureOptions.
        """
        GetDllLibOcr().ConfigureOptions_get_AutoRotate.argtypes = [c_void_p]
        GetDllLibOcr().ConfigureOptions_get_AutoRotate.restype = c_bool
        ret = CallCFunction(GetDllLibOcr().ConfigureOptions_get_AutoRotate,self.Ptr)
        return ret

    @AutoRotate.setter
    def AutoRotate(self, value: bool):
        """
        Set the automatic image rotation of the Ocr ConfigureOptions.
        """
        GetDllLibOcr().ConfigureOptions_set_AutoRotate.argtypes = [c_void_p, c_bool]
        CallCFunction(GetDllLibOcr().ConfigureOptions_set_AutoRotate,self.Ptr, value)

   