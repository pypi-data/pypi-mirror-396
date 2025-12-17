from tigerasm import TigerASM
from time import time as t


# -------- Python Inline Assembly ----------

asm = TigerASM()

code = """
    mov rax, 0
    mov rbx, 10

loop:
    add rax, rbx
    dec rbx
    jnz loop
    ret
"""

asm.asm(code)
start = t()
asm.execute()
stop = t() - start
print(f"RAX = {asm.get('rax')}, Take = {stop}s to run")
asm.clear()

# ------------- Condition --------

code = """

    cmp rcx, 2
    jne .else 
    inc rcx   
    jmp .fi   

.else:        
    dec rcx   

.fi:          
    ; ... 
"""

asm.asm(code)
asm.execute()
print(asm.get('rcx'))
asm.clear()

from tigerasm import TigerASM
from time import time as t

asm = TigerASM()

asm.asm("""
    mov rax, 0
    mov rbx, 1000000
loop:
    dec rbx
    jnz loop
    ret
""")

start = t()
asm.execute()
stop = t() - start
print(f"Time to run: {stop}s")
