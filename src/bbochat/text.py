"""
Text module that merges psiutils.text.strings with project-level strings.

Usage:
    from text_module import Text

    txt = Text()
    print(txt.SELECT)   # Access as attribute
    print(txt.DELETE_PROMPT)
"""

from dataclasses import dataclass, field
from psiutils.text import Text as PsiText

CONFIG = 'Settings'
strings = {
    'ACCEPT': 'Accept',
    'CHEVRON_UP': '\u25B4',
    'CHEVRON_DOWN': '\u25BE',
    'CONFIG': CONFIG,
    'EDIT_ALL': 'Edit all',
    'EDIT_ITEM': 'Edit item',
    'DELETE_RECORD': 'Are you sure you wish to delete this record?',
    'DELETE_ITEM': 'Are you sure you wish to delete this item?',
    'DELETE_PAIR': 'Are you sure you wish to delete this pair?',
    'DELETE_TITLE': 'Delete item',
    'MOVE_UP': 'Move up',
    'MOVE_DOWN': 'Move down',
    'REPORT_HELP': """
    'To format board number in the report, enter board number as 'b1'. etc.; \n
    'to display suit symbols in the report, enter suits as '!s', '!h' etc.
    '""",
    'RESTORE': 'Restore defaults',
    'SELECT': 'Select',
    'TOOLTIP': f"""
    'To insert your partner's and your names, use '<names>';\n
    'to insert your opponents' names, use '<opps>';\n
    'to insert your system, use '<system>'.\n
    '(To remove this hint goto {CONFIG}).
    '""",
}


@dataclass
class Text:
    """Combines package-level (psiutils) and project-level strings.

    Attributes from `psiutils.text.strings` are loaded first, then overridden
    or extended by the local `strings` dictionary.
    """

    display: bool = field(default=False, repr=False)

    def __post_init__(self) -> None:
        """Populate the dataclass instance with string attributes."""
        # Load psiutils strings
        psi_text = PsiText()
        psi_strings = psi_text.strings
        for key, string in psi_strings.items():
            setattr(self, key, string)

        # Override or add project-level strings
        for key, string in strings.items():
            setattr(self, key, string)

        # Optionally display contents of `text`
        if self.display:
            psi_text.display(strings)
