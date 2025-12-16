from enum import Enum

class TextBlockType(Enum):
    """
    Text block type, line, word or character
    """
    Line = 0
    Word = 1
    Character = 2
