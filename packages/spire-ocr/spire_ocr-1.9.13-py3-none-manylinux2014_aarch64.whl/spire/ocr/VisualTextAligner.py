from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.ocr.common import *
from spire.ocr import *
#from spire.ocr import OCRTTT
from ctypes import *

class VisualTextAligner(SpireObject):
    """
    Represents interface that work with ocr result text.
    """

    def __init__(self, ocrText:OCRText):
        intPtrOcrText:c_void_p = ocrText.Ptr
        GetDllLibOcr().VisualTextAligner_Create.argtypes=[c_void_p]
        GetDllLibOcr().VisualTextAligner_Create.restype = c_void_p
        intPtr = CallCFunction(GetDllLibOcr().VisualTextAligner_Create,intPtrOcrText)
        super(VisualTextAligner, self).__init__(intPtr)


    def ToString(self) -> str:
        """
        Gets whole ocr result plain text without formatting.
        """
        GetDllLibOcr().VisualTextAligner_ToString.argtypes = [c_void_p]
        GetDllLibOcr().VisualTextAligner_ToString.restype = c_void_p
        strIntPtr = CallCFunction(GetDllLibOcr().VisualTextAligner_ToString,self.Ptr)
        ret = PtrToStr(strIntPtr)
        return ret

    @property
    def Blocks(self) -> List["OCRTextBlock"]:
        """
        Gets an array of ocr result text by blocks.
        """
        GetDllLibOcr().VisualTextAligner_get_Blocks.argtypes = [c_void_p]
        GetDllLibOcr().VisualTextAligner_get_Blocks.restype = IntPtrArray

        intPtrArr = CallCFunction(GetDllLibOcr().VisualTextAligner_get_Blocks,self.Ptr)
        ret = None if intPtrArr == None else GetObjVectorFromArray(intPtrArr, OCRTextBlock)
        return ret