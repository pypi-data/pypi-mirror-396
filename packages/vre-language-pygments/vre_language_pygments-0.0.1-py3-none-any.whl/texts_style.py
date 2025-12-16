"""Pygments plugin style for textS/textM"""
from pygments.style import Style
from pygments.token import Keyword


class TextSStyle(Style):
    """This style merely highlights keywords in red"""
    styles = {
        Keyword: '#f00',
    }
