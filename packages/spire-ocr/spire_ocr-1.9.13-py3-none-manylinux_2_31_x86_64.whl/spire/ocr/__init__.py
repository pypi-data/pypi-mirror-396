import sys
from ctypes import *
from spire.ocr.common import *
from spire.ocr.common import dlllib
from spire.ocr.common import dlllibOcr

#from spire.ocr.common.SpireObject import SpireObjec

from spire.ocr.common.Common import IntPtrArray
from spire.ocr.common.Common import IntPtrWithTypeName
from spire.ocr.common.Common import GetObjVectorFromArray
from spire.ocr.common.Common import GetStrVectorFromArray
from spire.ocr.common.Common import GetVectorFromArray
from spire.ocr.common.Common import GetIntPtrArray
from spire.ocr.common.Common import GetByteArray
from spire.ocr.common.Common import GetIntValue
from spire.ocr.common.Common import GetObjIntPtr

from spire.ocr.common.RegexOptions import RegexOptions
from spire.ocr.common.CultureInfo import CultureInfo
from spire.ocr.common.Boolean import Boolean
from spire.ocr.common.Byte import Byte
from spire.ocr.common.Char import Char
from spire.ocr.common.Int16 import Int16
from spire.ocr.common.Int32 import Int32
from spire.ocr.common.Int64 import Int64
from spire.ocr.common.PixelFormat import PixelFormat
from spire.ocr.common.Size import Size
from spire.ocr.common.SizeF import SizeF
from spire.ocr.common.Point import Point
from spire.ocr.common.PointF import PointF
from spire.ocr.common.Rectangle import Rectangle
from spire.ocr.common.RectangleF import RectangleF
from spire.ocr.common.Single import Single
from spire.ocr.common.TimeSpan import TimeSpan
from spire.ocr.common.UInt16 import UInt16
from spire.ocr.common.UInt32 import UInt32
from spire.ocr.common.UInt64 import UInt64
from spire.ocr.common.Stream import Stream
from spire.ocr.common.License import License
from spire.ocr.common.Color import Color
from spire.ocr.common.DateTime import DateTime
from spire.ocr.common.Double import Double
from spire.ocr.common.EmfType import EmfType
from spire.ocr.common.Encoding import Encoding
from spire.ocr.common.FontStyle import FontStyle
from spire.ocr.common.GraphicsUnit import GraphicsUnit
from spire.ocr.common.ICollection import ICollection
from spire.ocr.common.IDictionary import IDictionary
from spire.ocr.common.IEnumerable import IEnumerable
from spire.ocr.common.IEnumerator import IEnumerator
from spire.ocr.common.IList import IList
from spire.ocr.common.String import String
from spire.ocr.common.Regex import Regex

from spire.ocr.license.LicenseProvider import LicenseProvider 
from spire.ocr.TextBlockType import TextBlockType
from spire.ocr.OCRImageFormat import OCRImageFormat
from spire.ocr.ConfigureOptions import ConfigureOptions
from spire.ocr.OCRTextBlock import OCRTextBlock
from spire.ocr.OCRText import OCRText
from spire.ocr.OcrScanner import OcrScanner
from spire.ocr.VisualTextAligner import VisualTextAligner

