from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.ocr.common import *
from spire.ocr import *
from ctypes import *

class OCRTextBlock(SpireObject):
    """
    Represents Interface that information about each block of the ocr result text.
    """

    @property
    def Box(self) -> Rectangle:
        """
        Gets the rectangular area where the detected block Coordinates starts with the upper left corner of the image.
        """
        GetDllLibOcr().IOCRTextBlock_get_Box.argtypes = [c_void_p]
        GetDllLibOcr().IOCRTextBlock_get_Box.restype = c_void_p
        ret = Rectangle(CallCFunction(GetDllLibOcr().IOCRTextBlock_get_Box,self.Ptr))
        return ret

    @property
    def Text(self) -> str:
        """
        Gets the text of this block.
        """
        GetDllLibOcr().IOCRTextBlock_get_Text.argtypes = [c_void_p]
        GetDllLibOcr().IOCRTextBlock_get_Text.restype = c_void_p

        strIntPtr = CallCFunction(GetDllLibOcr().IOCRTextBlock_get_Text,self.Ptr)
        ret = PtrToStr(strIntPtr)
        return ret

    @property
    def Confidence(self) -> float:
        """
        value can be from 0.0 to 1.0 inclusive. Value 0.0 means that the poorly recognized, 
        1.0 means that perfectly recognized.
        """
        GetDllLibOcr().IOCRTextBlock_get_Confidence.argtypes = [c_void_p]
        GetDllLibOcr().IOCRTextBlock_get_Confidence.restype = c_float
        ret = CallCFunction(GetDllLibOcr().IOCRTextBlock_get_Confidence,self.Ptr)
        return ret

    @property
    def TextBlock(self) -> List["OCRTextBlock"]:
        """
        Array of lower level text block
        (e.g. words or characters)
        """
        GetDllLibOcr().IOCRTextBlock_get_TextBlock.argtypes = [c_void_p]
        GetDllLibOcr().IOCRTextBlock_get_TextBlock.restype = IntPtrArray

        intPtrArr = CallCFunction(GetDllLibOcr().IOCRTextBlock_get_TextBlock,self.Ptr)
        ret = None if intPtrArr == None else GetObjVectorFromArray(intPtrArr, OCRTextBlock)
        return ret

    @property
    def Level(self) -> 'TextBlockType':
        """
        Text block type of text block.
        """
        GetDllLibOcr().IOCRTextBlock_get_Level.argtypes = [c_void_p]
        GetDllLibOcr().IOCRTextBlock_get_Level.restype = c_int
        intV = CallCFunction(GetDllLibOcr().IOCRTextBlock_get_Level,self.Ptr);
        ret = TextBlockType(intV)
        return ret

    @property
    def IsTruncated(self) -> bool:
        """
        Indicates whether result was truncated due to evaluation limited
        """
        GetDllLibOcr().IOCRTextBlock_get_IsTruncated.argtypes = [c_void_p]
        GetDllLibOcr().IOCRTextBlock_get_IsTruncated.restype = c_bool
        ret = CallCFunction(GetDllLibOcr().IOCRTextBlock_get_IsTruncated,self.Ptr)
        return ret