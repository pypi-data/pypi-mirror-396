# pygments-plugin-texts

This is a plugin for the [Pygments package](https://pygments.org/) providing
a lexer, formatter, filter and style for the
[VRE-Language](https://gitlab.kit.edu/kit/virtmat-tools/vre-language)
family of languages (currently textS and textM).

## Run the lexer

Via CLI:
```bash
pygmentize -l texts test.vm
```
The lexer class can be imported directly using
```python
from texts_lexer import TextSLexer
```

## Run the formatter

Via CLI:
```bash
pygmentize -f texts-format test.vm
```

Retrieve the formatter class via the API with
```python
formatter_class = pygments.formatters.find_formatter_class("texts-format")
```

## Run the style

Via CLI:
```bash
pygmentize -O style=texts-style
```

Retrieve the style class via API with
```python
style_class = pygments.styles.get_style_by_name('texts-style')
```

## Run the filter

Via CLI:
```bash
pygmentize -F texts-filter
```
Retrieve the filter class via API with
```python
filter_class = pygments.filters.find_filter_class('texts-filter')
```

## Run the tests

After installing the plugin, the tests can be run by these commands:

```bash
pygmentize -l textm test_1.vm
pygmentize -l textm test_2.vm
```
