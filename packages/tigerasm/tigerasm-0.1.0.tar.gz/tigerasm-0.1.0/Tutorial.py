from tigerasm import TigerASM

asm = TigerASM()

code = """
    mov rax, 0
    mov rbx, 100

loop:
    add rax, rbx
    dec rbx
    ret
"""

asm.asm(code)
asm.execute()
print(asm.get('rax'))
print(asm.get('rbx'))