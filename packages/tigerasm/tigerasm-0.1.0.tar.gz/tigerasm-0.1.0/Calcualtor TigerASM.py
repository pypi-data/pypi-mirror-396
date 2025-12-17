from tigerasm import TigerASM

class Calculator:
    def __init__(self):
        self.asm = TigerASM()

    def add(self, a: int, b: int) -> int:
        self.asm.clear()
        self.asm.clear_memory()
        self.asm.mov('rax', a)
        self.asm.mov('rbx', b)

        code = """
                add rax, rbx
                ret
            """

        self.asm.asm(code)
        self.asm.execute()
        return self.asm.get('rax')

    def sub(self, a: int, b: int) -> int:
        self.asm.clear()
        self.asm.clear_memory()
        self.asm.mov('rax', a)
        self.asm.mov('rbx', b)

        code = """
                sub rax, rbx
                ret
            """

        self.asm.asm(code)
        self.asm.execute()
        return self.asm.get('rax')

    def multiple(self, a: int, b: int) -> int:
        self.asm.clear()
        self.asm.clear_memory()
        self.asm.mov('rax', a)
        self.asm.mov('rbx', b)

        code = """
                imul rax, rbx
                ret
            """

        self.asm.asm(code)
        self.asm.execute()
        return self.asm.get('rax')

    def divide(self, a, b):
        self.asm.clear()
        self.asm.clear_memory()
        self.asm.mov('rax', a)
        self.asm.mov('rbx', b)

        self.asm.asm("""
            mov rdx, 0
            div rbx
            ret
        """)
        self.asm.execute()
        return self.asm.get('rax')


    def _input(self, prompt: str, _type: object, /) -> object:
        while True:
            try: return _type(input(prompt)); break
            except: continue

    def calculate(self) -> None:
        a: int = self._input("Enter 1st number (in int64): ", int)
        b: int = self._input("Enter 2nd number (in int64): ", int)
        c: str = self._input("Enter operator (+, -, *, /): ", str)

        match c:
            case "+": print(self.add(a, b))
            case "-": print(self.sub(a, b))
            case "*": print(self.multiple(a, b))
            case "/": print(self.divide(a, b))
            case _: print('Invalid Option!', flash= True)

if __name__ == "__main__":
    calculator = Calculator()
    calculator.calculate()
