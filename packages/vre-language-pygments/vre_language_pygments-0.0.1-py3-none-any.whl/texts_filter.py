"""Pygments filter plugin for textS/textM"""
from pygments.filters import Filter


class TextSFilter(Filter):
    """This filter replaces all tabs with '<tab>'"""
    def filter(self, lexer, stream):
        for ttype, value in stream:
            parts = value.split('\t')
            yield ttype, '<tab>'.join(parts)
