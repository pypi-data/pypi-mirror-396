from enum import Enum


class TextFormat(Enum):
    PLAIN = "PLAIN"
    HTML = "HTML"
    RST = "RST"
    MARKDOWN = "MARKDOWN"
    JSON = "JSON"
    KEEP_MARKDOWN = "KEEP_MARKDOWN"
    JSONL = "JSONL"
    PLAIN_BLANKLINE_SPLIT = "PLAIN_BLANKLINE_SPLIT"
