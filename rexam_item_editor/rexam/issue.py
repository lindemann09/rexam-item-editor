from dataclasses import dataclass, field
from typing import Any, Callable

@dataclass
class Issue(object):
    # issues from the validations

    label: str
    description: str
    fix_fnc: Any = field(default=None)
    fix_requires_gui_reset: bool = field(default=False)

    def has_fix_function(self):
        return isinstance(self.fix_fnc, Callable)

    def fix(self):
        if self.has_fix_function():
            return self.fix_fnc()
        else:
            return False