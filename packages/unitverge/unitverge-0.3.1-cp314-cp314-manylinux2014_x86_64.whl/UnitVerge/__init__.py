'''
# UnitVerge Framework
'''

__version__ = '0.7'

'UV - UNITVERGE'
from .Verge import Verge as Verge
from .Verge.Basics.syntax import SForm as SForm
from .Verge import UVObj
from .Verge import Unit as Unit

class Bytex:
    _current = '2.0'
    def get(self):
        from .Bytex import get_from_ver
        return get_from_ver(self._current)()
    @property
    def current(self):
        from .Bytex.bx2 import lang
        return lang()
    def exec_main(
        self, 
        code: list [str] | str, 
        main_method: str = 'main'
    ) -> dict:
        if isinstance(code, list): code = '\n'.join(code)
        code += f'\ndo {main_method}'
        return self.current['ex'](code)
    @property
    def translator(self):
        from .Bytex.bx2 import Translator
        return Translator