"""pygments plugin formatter for the textS/textM languages"""
from pygments.formatter import Formatter


class TextSFormatter(Formatter):
    """the texts formatter class"""
    name = 'textS/textM Format'
    aliases = ['texts-format']
    # This is a list of file patterns that the formatter will
    # typically be used to produce. In this example, calling
    #
    #   pygmentize -o out.textsfmt
    #
    # will automatically select this formatter based on the output
    # file name. Similarly,
    #
    #   pygments.formatters.get_formatter_for_filename("out.textsfmt")
    #
    # will return an instance of this formatter class.
    filenames = ['*.textsfmt']

    def format_unencoded(self, tokensource, out):
        """this formatter writes each token as [<color>]<string>"""
        for ttype, value in tokensource:
            while not self.style.styles_token(ttype):
                ttype = ttype.parent
            color = self.style.style_for_token(ttype)['color']
            out.write('[' + (color or 'black') + ']')
            out.write(value)
