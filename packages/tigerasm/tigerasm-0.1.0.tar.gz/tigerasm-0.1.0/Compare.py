import time
import numpy as np
from tigerasm import TigerASM

# ---------------------------------
# 1️⃣ Pure Python loop
# ---------------------------------
N = 1_000_000
start = time.time()
x = 0
for i in range(N):
    x += 1
stop = time.time()
print(f"[Python]   x={x}, Time={stop-start:.6f}s")

# ---------------------------------
# 2️⃣ NumPy vectorized
# ---------------------------------
start = time.time()
arr = np.arange(1, N+1)
y = np.sum(arr) - np.sum(arr-1)  # just to keep operation simple
stop = time.time()
print(f"[NumPy]    y={y}, Time={stop-start:.6f}s")

# ---------------------------------
# 3️⃣ TigerASM native loop
# ---------------------------------
asm = TigerASM()
asm.asm(f"""
    mov rax, 0
    mov rbx, {N}
loop:
    inc rax
    dec rbx
    jnz loop
    ret
""")

start = time.time()
asm.execute()
stop = time.time()
rax_value = asm.get('rax')
print(f"[TigerASM] rax={rax_value}, Time={stop-start:.6f}s")

asm.clear()
