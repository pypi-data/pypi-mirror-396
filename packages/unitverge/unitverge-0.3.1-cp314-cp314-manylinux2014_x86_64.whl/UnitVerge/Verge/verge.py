from .Basics._base import UVObj




class Verge:
    def __init__(self) -> None:
        self.instruction = {
            'generatable':{'type':'build', 'getcode':'get_code'},
            'builder':{'type':'edit', 'inst_attr':'INSTRUCTIONS'},
        }
        self.type = {
            'build': self.build,
            'edit': self.edit,
        }
        self.code = []
    
    def interprete(self, instructions: list):
        if not isinstance(instructions, (list, tuple)):
            raise TypeError(f"instructions must be list, got {type(instructions)}")
        ins: object
        for ins in instructions:
            ins_type = repr(ins)
            if not ins_type.startswith('instruction-'):
                raise ValueError(f'Bad instruction {repr(ins)}')
            try: ins_type = ins.name
            except: raise ValueError(f'Bad instruction {repr(ins)} : has no attribute name.')
            if ins_type in self.instruction.keys():
                self.work(ins, ins_type)
            else: 
                raise ValueError(f'Instruction {repr(ins)} ({ins_type}) not in Verge instructions')
    
    def work(self, instruction: object, typ: str):
        type = self.instruction[typ]['type']
        try: handler = self.type[type]
        except:
            raise ValueError(f'Bad instruction {repr(instruction)} : unknown type {type} : has no handler.')
        handler(instruction, typ)

    def build(self, ins: object, typ: str):
        try: method = self.instruction[typ]['getcode']
        except: raise ValueError(f'Bad instruction {repr(ins)} : has no key getcode with name of attribute.')
        attr = ins.__getattribute__(method)
        try: code = attr()
        except Exception as e:
            raise ValueError(f'Bad instruction {repr(ins)} : error in handler : {e}')
        if not isinstance(code, list):
            raise ValueError(f'Bad handler : returning type is {type(code)}, but must be list')
        for line in code: self.code.append(line)
    
    def edit(self, ins: object, typ: str):
        try: method = self.instruction[typ]['INSTRUCTIONS']
        except: raise ValueError(f'Bad instruction {repr(ins)} : has no key INSTRUCTIONS with list of instructions.')
        attr = ins.__getattribute__(method)
        if not isinstance(attr, list):
            raise ValueError(f'Bad instruction {repr(ins)} : INSTRUCTIONS must be list, not {type(attr)}.')
        for sub_ins in attr:
            try: sub_ins(self)
            except Exception as e: 
                raise ValueError(f'Bad instruction {repr(sub_ins)} : bad INSTRUCTIONS for Verge : {e}.')

    def compile(self):
        return self.code