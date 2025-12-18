import re
import logging

# FIXME to be improved
VAR_REF = re.compile(
    # NOTE probably pg specific?
    r'(?P<dquote>"(""|[^"])+")|'
    # FIXME mysql/mariadb use backslash escapes
    r"(?P<squote>\'(\'\'|[^\'])*\')|"
    # NOTE beware of overlapping re
    r"([\s]+):(?P<var_name>\w+)(?=[^:]?)"
)
"""Pattern to identify colon-variables (aka _named_ style) in SQL code"""

# NOTE see comments above
VAR_REF_DOT = re.compile(
    r'(?P<dquote>"(""|[^"])+")|'
    r"(?P<squote>\'(\'\'|[^\'])*\')|"
    r"([\s]+):(?P<var_name>\w+\.\w+)(?=[^:]?)"
    # FIXME: ensure SPARQL prefix are not taken into account as ouisparql variable
    # r"(?P<lead>[^:]):(?P<var_name>\w+\.\w+)(?=[^:]?)"
)
"""Pattern to identify colon-variables with a simple attribute in SQL code."""

log = logging.getLogger("aiosql")
"""Shared package logging."""
# log.setLevel(logging.DEBUG)


class SPARQLLoadException(Exception):
    """Raised when there is a problem loading SPARQL content from a file or directory"""

    pass


class SPARQLParseException(Exception):
    """Raised when there was a problem parsing the ouisparql comment annotations in SPARQL"""

    pass

def to_string_literal(word: str) -> str:
    return f'"{word}"'
