from tigerasm import TigerASM

# Test 1: Empty ret
asm = TigerASM()
asm.asm("ret")
asm.execute()
print("✓ Test 1 passed")

# Test 2: Set register
asm = TigerASM()
asm.asm("mov rax, 42; ret")
asm.execute()
assert asm.get('rax') == 42
print("✓ Test 2 passed")

# Test 3: Addition
asm = TigerASM()
asm.mov('rax', 10)
asm.mov('rbx', 20)
asm.asm("add rax, rbx; ret")
asm.execute()
assert asm.get('rax') == 30
print("✓ Test 3 passed")

# Test 4: Loop
asm = TigerASM()
asm.asm("""
    mov rax, 0
    mov rcx, 10
loop:
    add rax, rcx
    dec rcx
    jnz loop
    ret
""")
asm.execute()
assert asm.get('rax') == 55
print("✓ Test 4 passed")

print("\n✓ All tests passed! TigerASM is working correctly!")

asm = TigerASM()

def add(a, b):
    asm.clear()  # Reset previous code and labels
    asm.asm(f"""
        mov rax, {int(a)}
        mov rbx, {int(b)}
        add rax, rbx
        ret
    """)
    asm.execute()
    return asm.get("rax")

def mul(a, b):
    asm.clear()
    asm.asm(f"""
        mov rax, {int(a)}
        mov rbx, {int(b)}
        imul rax, rbx
        ret
    """)
    asm.execute()
    return asm.get("rax")

print(add(5, 7))   # 12
print(mul(6, 8))   # 48

print(add(986,789))
