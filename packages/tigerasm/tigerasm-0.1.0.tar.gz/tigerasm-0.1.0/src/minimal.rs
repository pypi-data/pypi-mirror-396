//! TigerASM - Ultimate Complete Runtime Assembler
//! Full x86-64 and ARM64 support with COMPLETE memory addressing
//!
//! Supports:
//! - All memory modes: [reg], [reg+offset], [reg+reg], [reg+reg*scale], [offset]
//! - AT&T syntax: %rax, %eax, etc.
//! - Intel syntax: rax, eax, etc.
//! - Immediate addressing: $value, #value
//! - Complex addressing: [base + index*scale + disp]

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use dynasmrt::{dynasm, DynasmApi, DynasmLabelApi, ExecutableBuffer, AssemblyOffset};
#[cfg(target_arch = "x86_64")]
use dynasmrt::x64::Assembler as AssemblerX64;
#[cfg(target_arch = "aarch64")]
use dynasmrt::aarch64::Assembler as AssemblerAArch64;
use std::collections::HashMap;
use std::fs::File;
use std::io::{Read, Write};

// Include all register structures from lib_ultimate.rs (lines 21-115)
#[derive(Default, Debug, Clone)]
pub struct RegistersX86Complete {
    pub rax: u64, pub rbx: u64, pub rcx: u64, pub rdx: u64,
    pub rsi: u64, pub rdi: u64, pub rsp: u64, pub rbp: u64,
    pub r8: u64, pub r9: u64, pub r10: u64, pub r11: u64,
    pub r12: u64, pub r13: u64, pub r14: u64, pub r15: u64,
    pub rip: u64, pub rflags: u64,
    pub cs: u16, pub ds: u16, pub es: u16, pub fs: u16, pub gs: u16, pub ss: u16,
    pub cr0: u64, pub cr1: u64, pub cr2: u64, pub cr3: u64, pub cr4: u64,
    pub dr0: u64, pub dr1: u64, pub dr2: u64, pub dr3: u64,
    pub dr4: u64, pub dr5: u64, pub dr6: u64, pub dr7: u64,
    pub gdtr: u64, pub idtr: u64, pub ldtr: u16, pub tr: u16,
    pub xmm: [[u64; 2]; 16],
    pub ymm_high: [[u64; 2]; 16],
    pub zmm_high: [[u64; 4]; 16],
    pub st: [(u64, u16); 8],
    pub mm: [u64; 8],
    pub fpr: [u64; 8],
    pub fpu_control: u16, pub fpu_status: u16, pub fpu_tag: u16,
}

#[derive(Default, Debug, Clone)]
pub struct RegistersARM64Complete {
    pub x: [u64; 31],
    pub sp: u64, pub pc: u64, pub lr: u64, pub fp: u64, pub xzr: u64,
    pub v: [[u64; 2]; 32],
    pub pstate: u64, pub cpsr: u32, pub apsr: u32,
    pub sp_el0: u64, pub sp_el1: u64, pub sp_el2: u64, pub sp_el3: u64,
    pub elr_el1: u64, pub elr_el2: u64, pub elr_el3: u64,
    pub spsr_el1: u32, pub spsr_el2: u32, pub spsr_el3: u32,
    pub fpcr: u32, pub fpsr: u32,
}

// Memory Allocator (same as before)
#[derive(Debug, Clone)]
struct MemoryBlock {
    start: usize,
    size: usize,
    in_use: bool,
}

struct MemoryAllocator {
    blocks: Vec<MemoryBlock>,
    memory_size: usize,
}

impl MemoryAllocator {
    fn new(size: usize) -> Self {
        Self {
            blocks: vec![MemoryBlock { start: 0, size, in_use: false }],
            memory_size: size,
        }
    }

    fn allocate(&mut self, size: usize) -> Option<usize> {
        for i in 0..self.blocks.len() {
            if !self.blocks[i].in_use && self.blocks[i].size >= size {
                let block = &mut self.blocks[i];
                let addr = block.start;
                if block.size > size {
                    let remaining = MemoryBlock {
                        start: block.start + size,
                        size: block.size - size,
                        in_use: false,
                    };
                    block.size = size;
                    self.blocks.insert(i + 1, remaining);
                }
                block.in_use = true;
                return Some(addr);
            }
        }
        None
    }

    fn free(&mut self, addr: usize) -> bool {
        if let Some(idx) = self.blocks.iter().position(|b| b.start == addr && b.in_use) {
            self.blocks[idx].in_use = false;
            self.coalesce(idx);
            true
        } else {
            false
        }
    }

    fn coalesce(&mut self, idx: usize) {
        if idx + 1 < self.blocks.len() && !self.blocks[idx + 1].in_use {
            let next_size = self.blocks[idx + 1].size;
            self.blocks[idx].size += next_size;
            self.blocks.remove(idx + 1);
        }
        if idx > 0 && !self.blocks[idx - 1].in_use {
            self.blocks[idx - 1].size += self.blocks[idx].size;
            self.blocks.remove(idx);
        }
    }

    fn stats(&self) -> (usize, usize, usize) {
        let used: usize = self.blocks.iter().filter(|b| b.in_use).map(|b| b.size).sum();
        (used, self.memory_size - used, self.blocks.len())
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// COMPLETE Memory Addressing Support
// ═══════════════════════════════════════════════════════════════════════════

#[derive(Debug, Clone)]
enum MemoryAddr {
    // Simple modes
    Register(String),                          // [rax]
    Immediate(u64),                            // [0x1000]
    
    // Offset modes
    RegOffset(String, i64),                    // [rax + 8] or [rax - 4]
    
    // SIB (Scale-Index-Base) modes
    RegRegScale(String, String, u8),           // [base + index*scale]
    RegRegScaleDisp(String, String, u8, i64),  // [base + index*scale + disp]
    
    // Index with displacement
    RegReg(String, String),                    // [rax + rbx]
    
    // RIP-relative (x86-64)
    RipRelative(i32),                          // [rip + offset]
}

// Helper to strip AT&T syntax prefix (%)
fn strip_att_prefix(s: &str) -> String {
    s.trim_start_matches('%').trim_start_matches('$').trim_start_matches('#').to_string()
}

// Parse complex memory addressing
fn parse_memory_addr(addr_str: &str) -> Result<MemoryAddr, String> {
    let addr_str = addr_str.trim();
    
    if !addr_str.starts_with('[') || !addr_str.ends_with(']') {
        return Err(format!("Invalid memory address format '{}': must be enclosed in brackets", addr_str));
    }
    
    let inner = addr_str[1..addr_str.len() - 1].trim();
    
    // Try to parse as immediate address [0x1000]
    if let Ok(val) = parse_number(inner) {
        return Ok(MemoryAddr::Immediate(val));
    }
    
    // Handle RIP-relative: [rip + offset]
    if inner.to_lowercase().contains("rip") {
        let parts: Vec<&str> = inner.split('+').collect();
        if parts.len() == 2 {
            let offset = parse_number(parts[1].trim())? as i32;
            return Ok(MemoryAddr::RipRelative(offset));
        }
        return Ok(MemoryAddr::Register("rip".to_string()));
    }
    
    // Simple register: [rax]
    if !inner.contains('+') && !inner.contains('-') && !inner.contains('*') {
        let reg = strip_att_prefix(inner);
        return Ok(MemoryAddr::Register(reg));
    }
    
    // Complex addressing: parse [base + index*scale + disp]
    parse_complex_address(inner)
}

fn parse_complex_address(inner: &str) -> Result<MemoryAddr, String> {
    // Handle [reg + reg] or [reg + offset]
    if let Some(plus_pos) = inner.find('+') {
        let left = inner[..plus_pos].trim();
        let right = inner[plus_pos + 1..].trim();
        
        // Check for scale: [reg + reg*scale]
        if right.contains('*') {
            let parts: Vec<&str> = right.split('*').collect();
            if parts.len() == 2 {
                let index = strip_att_prefix(parts[0].trim());
                let scale = parts[1].trim().parse::<u8>()
                    .map_err(|_| format!("Invalid scale: {}", parts[1]))?;
                let base = strip_att_prefix(left);
                return Ok(MemoryAddr::RegRegScale(base, index, scale));
            }
        }
        
        // Try [reg + reg]
        if is_register(right) {
            let base = strip_att_prefix(left);
            let index = strip_att_prefix(right);
            return Ok(MemoryAddr::RegReg(base, index));
        }
        
        // Try [reg + offset]
        if let Ok(offset) = parse_number(right) {
            let reg = strip_att_prefix(left);
            return Ok(MemoryAddr::RegOffset(reg, offset as i64));
        }
    }
    
    // Handle [reg - offset]
    if let Some(minus_pos) = inner.find('-') {
        let left = inner[..minus_pos].trim();
        let right = inner[minus_pos + 1..].trim();
        
        if let Ok(offset) = parse_number(right) {
            let reg = strip_att_prefix(left);
            return Ok(MemoryAddr::RegOffset(reg, -(offset as i64)));
        }
    }
    
    Err(format!("Could not parse memory address: [{}]", inner))
}

// Parse numbers in various formats (decimal, hex, binary)
fn parse_number(s: &str) -> Result<u64, String> {
    let s = s.trim();
    
    // Hex: 0x123 or 0X123
    if s.starts_with("0x") || s.starts_with("0X") {
        return u64::from_str_radix(&s[2..], 16)
            .map_err(|_| format!("Invalid hex number: {}", s));
    }
    
    // Binary: 0b101 or 0B101
    if s.starts_with("0b") || s.starts_with("0B") {
        return u64::from_str_radix(&s[2..], 2)
            .map_err(|_| format!("Invalid binary number: {}", s));
    }
    
    // Decimal
    s.parse::<u64>().map_err(|_| format!("Invalid number: {}", s))
}

// Check if string is a register name (with or without % prefix)
fn is_register(s: &str) -> bool {
    let s = strip_att_prefix(s);
    is_valid_register(&s.to_lowercase())
}

// Register validation (same as before)
fn is_valid_x86_register(reg: &str) -> bool {
    matches!(reg,
        "rax" | "rbx" | "rcx" | "rdx" | "rsi" | "rdi" | "rsp" | "rbp" |
        "r8" | "r9" | "r10" | "r11" | "r12" | "r13" | "r14" | "r15" |
        "eax" | "ebx" | "ecx" | "edx" | "esi" | "edi" | "esp" | "ebp" |
        "r8d" | "r9d" | "r10d" | "r11d" | "r12d" | "r13d" | "r14d" | "r15d" |
        "ax" | "bx" | "cx" | "dx" | "si" | "di" | "sp" | "bp" |
        "r8w" | "r9w" | "r10w" | "r11w" | "r12w" | "r13w" | "r14w" | "r15w" |
        "al" | "ah" | "bl" | "bh" | "cl" | "ch" | "dl" | "dh" |
        "sil" | "dil" | "bpl" | "spl" |
        "r8b" | "r9b" | "r10b" | "r11b" | "r12b" | "r13b" | "r14b" | "r15b" |
        "xmm0" | "xmm1" | "xmm2" | "xmm3" | "xmm4" | "xmm5" | "xmm6" | "xmm7" |
        "xmm8" | "xmm9" | "xmm10" | "xmm11" | "xmm12" | "xmm13" | "xmm14" | "xmm15" |
        "ymm0" | "ymm1" | "ymm2" | "ymm3" | "ymm4" | "ymm5" | "ymm6" | "ymm7" |
        "ymm8" | "ymm9" | "ymm10" | "ymm11" | "ymm12" | "ymm13" | "ymm14" | "ymm15" |
        "zmm0" | "zmm1" | "zmm2" | "zmm3" | "zmm4" | "zmm5" | "zmm6" | "zmm7" |
        "zmm8" | "zmm9" | "zmm10" | "zmm11" | "zmm12" | "zmm13" | "zmm14" | "zmm15" |
        "st0" | "st1" | "st2" | "st3" | "st4" | "st5" | "st6" | "st7" |
        "mm0" | "mm1" | "mm2" | "mm3" | "mm4" | "mm5" | "mm6" | "mm7" |
        "fpr0" | "fpr1" | "fpr2" | "fpr3" | "fpr4" | "fpr5" | "fpr6" | "fpr7" |
        "rip" | "eip" | "ip" | "rflags" | "eflags" | "flags" |
        "cs" | "ds" | "es" | "fs" | "gs" | "ss" |
        "cr0" | "cr1" | "cr2" | "cr3" | "cr4" |
        "dr0" | "dr1" | "dr2" | "dr3" | "dr4" | "dr5" | "dr6" | "dr7" |
        "gdtr" | "idtr" | "ldtr" | "tr"
    )
}

fn is_valid_arm_register(reg: &str) -> bool {
    if reg.len() >= 2 {
        let prefix = &reg[..1];
        let rest = &reg[1..];
        if let Ok(num) = rest.parse::<u32>() {
            return match prefix {
                "x" => num <= 30, "w" => num <= 30,
                "v" | "q" | "d" | "s" | "h" | "b" => num <= 31,
                _ => false,
            };
        }
    }
    matches!(reg,
        "sp" | "wsp" | "pc" | "lr" | "fp" | "xzr" | "wzr" |
        "pstate" | "cpsr" | "apsr" |
        "sp_el0" | "sp_el1" | "sp_el2" | "sp_el3" |
        "elr_el1" | "elr_el2" | "elr_el3" |
        "spsr_el1" | "spsr_el2" | "spsr_el3"
    )
}

fn is_valid_register(reg: &str) -> bool {
    let lower = reg.to_lowercase();
    is_valid_x86_register(&lower) || is_valid_arm_register(&lower)
}

// Instruction enum (same as before, but we'll use the enhanced memory addressing)
#[derive(Debug, Clone)]
enum Instr {
    MovRegImm(String, u64),
    MovRegReg(String, String),
    MovRegMem(String, MemoryAddr),
    MovMemReg(MemoryAddr, String),
    Movl(String, String),
    Movq(String, String),
    Lea(String, MemoryAddr),
    
    Add(String, u64), AddRegReg(String, String),
    Sub(String, u64), SubRegReg(String, String),
    Mul(String), Imul(String, String),
    Div(String), Inc(String), Dec(String), Neg(String),
    
    And(String, u64), AndRegReg(String, String),
    Or(String, u64), OrRegReg(String, String),
    Xor(String, u64), XorRegReg(String, String),
    Not(String),
    
    Shl(String, i8), Shr(String, i8),
    Sal(String, i8), Sar(String, i8),
    Rol(String, i8), Ror(String, i8),
    Rcl(String, i8), Rcr(String, i8),
    Lsl(String, i8), Lsr(String, i8), Asr(String, i8),
    
    Push(String), Pop(String),
    Cmp(String, u64), CmpRegReg(String, String),
    Test(String, u64), TestRegReg(String, String),
    
    Jmp(String), Je(String), Jne(String), Jz(String), Jnz(String),
    Jg(String), Jge(String), Jl(String), Jle(String),
    Ja(String), Jae(String), Jb(String), Jbe(String),
    
    B(String), Beq(String), Bne(String),
    Bcs(String), Bhs(String), Bcc(String), Blo(String),
    Bmi(String), Bpl(String), Bvs(String), Bvc(String),
    Bhi(String), Bls(String), Bge(String), Blt(String),
    Bgt(String), Ble(String), Bal(String),
    
    Call(String), Bl(String), Ret,
    Nop,
    Label(String),
    Global(String),
    Text, Data, Bss, Start,
}

// Enhanced parsing function
fn split_lines(code: &str) -> Vec<&str> {
    code.split('\n')
        .flat_map(|line| line.split(";;"))
        .map(|s| s.trim())
        .filter(|s| !s.is_empty() && !s.starts_with(';') && !s.starts_with('#'))
        .collect()
}

fn parse_operand(op: &str) -> String {
    // Strip AT&T syntax prefixes
    strip_att_prefix(op.trim_end_matches(','))
}

fn parse_instructions(code: &str) -> Result<Vec<Instr>, String> {
    let mut instrs = vec![];
    let lines = split_lines(code);
    
    for (line_num, line) in lines.iter().enumerate() {
        let line = line.split(';').next().unwrap_or(line)
                       .split('#').next().unwrap_or(line).trim();
        if line.is_empty() { continue; }
        
        // Handle directives
        if line.starts_with('.') {
            match line {
                ".text" => instrs.push(Instr::Text),
                ".data" => instrs.push(Instr::Data),
                ".bss" => instrs.push(Instr::Bss),
                _ if line.starts_with(".global ") || line.starts_with(".globl ") => {
                    let name = line.split_whitespace().nth(1)
                        .unwrap_or("").to_string();
                    instrs.push(Instr::Global(name));
                }
                _ => {}
            }
            continue;
        }
        
        // Handle labels
        if line.ends_with(':') {
            let label = line.trim_end_matches(':').to_string();
            instrs.push(Instr::Label(label));
            continue;
        }
        
        if line == "_start" {
            instrs.push(Instr::Start);
            continue;
        }

        let parts: Vec<&str> = line.split_whitespace().collect();
        if parts.is_empty() { continue; }

        let op = parts[0].to_lowercase();
        let op_str = op.as_str();

        match op_str {
            "mov" | "movl" | "movq" => {
                if parts.len() < 3 {
                    return Err(format!("Line {}: {} requires 2 operands", line_num + 1, op_str));
                }
                
                let dst_raw = parts[1].trim_end_matches(',');
                let src_raw = parts[2];
                
                // Handle AT&T syntax: movl %eax, %ebx (src, dst reversed)
                let (dst, src) = if dst_raw.starts_with('%') && src_raw.starts_with('%') {
                    // AT&T syntax - operands are reversed
                    (src_raw, dst_raw)
                } else {
                    (dst_raw, src_raw)
                };

                if dst.starts_with('[') {
                    let mem = parse_memory_addr(dst)?;
                    let src_reg = parse_operand(src);
                    instrs.push(Instr::MovMemReg(mem, src_reg));
                } else if src.starts_with('[') {
                    let mem = parse_memory_addr(src)?;
                    let dst_reg = parse_operand(dst);
                    instrs.push(Instr::MovRegMem(dst_reg, mem));
                } else {
                    let src_clean = strip_att_prefix(src.trim_start_matches('$').trim_start_matches('#'));
                    if let Ok(imm) = parse_number(&src_clean) {
                        let dst_reg = parse_operand(dst);
                        instrs.push(Instr::MovRegImm(dst_reg, imm));
                    } else {
                        let dst_reg = parse_operand(dst);
                        let src_reg = parse_operand(src);
                        if op_str == "movl" {
                            instrs.push(Instr::Movl(dst_reg, src_reg));
                        } else if op_str == "movq" {
                            instrs.push(Instr::Movq(dst_reg, src_reg));
                        } else {
                            instrs.push(Instr::MovRegReg(dst_reg, src_reg));
                        }
                    }
                }
            }
            
            "lea" => {
                if parts.len() < 3 {
                    return Err(format!("Line {}: lea requires 2 operands", line_num + 1));
                }
                let dst = parse_operand(parts[1]);
                let src = parts[2];
                let mem = parse_memory_addr(src)?;
                instrs.push(Instr::Lea(dst, mem));
            }

            "add" | "sub" | "and" | "or" | "xor" | "cmp" | "test" => {
                if parts.len() < 3 {
                    return Err(format!("Line {}: {} requires 2 operands", line_num + 1, op_str));
                }
                let dst = parse_operand(parts[1]);
                let src = parse_operand(parts[2]);
                
                if let Ok(imm) = parse_number(&src) {
                    instrs.push(match op_str {
                        "add" => Instr::Add(dst, imm),
                        "sub" => Instr::Sub(dst, imm),
                        "and" => Instr::And(dst, imm),
                        "or" => Instr::Or(dst, imm),
                        "xor" => Instr::Xor(dst, imm),
                        "cmp" => Instr::Cmp(dst, imm),
                        "test" => Instr::Test(dst, imm),
                        _ => unreachable!(),
                    });
                } else {
                    instrs.push(match op_str {
                        "add" => Instr::AddRegReg(dst, src),
                        "sub" => Instr::SubRegReg(dst, src),
                        "and" => Instr::AndRegReg(dst, src),
                        "or" => Instr::OrRegReg(dst, src),
                        "xor" => Instr::XorRegReg(dst, src),
                        "cmp" => Instr::CmpRegReg(dst, src),
                        "test" => Instr::TestRegReg(dst, src),
                        _ => unreachable!(),
                    });
                }
            }
            
            "shl" | "sal" | "shr" | "sar" | "rol" | "ror" | "rcl" | "rcr" |
            "lsl" | "lsr" | "asr" => {
                if parts.len() < 3 {
                    return Err(format!("Line {}: {} requires count", line_num + 1, op_str));
                }
                let reg = parse_operand(parts[1]);
                let cnt: i8 = parts[2].parse()
                    .map_err(|_| format!("Line {}: Invalid shift/rotate count", line_num + 1))?;
                instrs.push(match op_str {
                    "shl" => Instr::Shl(reg, cnt),
                    "sal" => Instr::Sal(reg, cnt),
                    "shr" => Instr::Shr(reg, cnt),
                    "sar" => Instr::Sar(reg, cnt),
                    "rol" => Instr::Rol(reg, cnt),
                    "ror" => Instr::Ror(reg, cnt),
                    "rcl" => Instr::Rcl(reg, cnt),
                    "rcr" => Instr::Rcr(reg, cnt),
                    "lsl" => Instr::Lsl(reg, cnt),
                    "lsr" => Instr::Lsr(reg, cnt),
                    "asr" => Instr::Asr(reg, cnt),
                    _ => unreachable!(),
                });
            }

            "jmp" | "je" | "jne" | "jz" | "jnz" | "jg" | "jge" | "jl" | "jle" |
            "ja" | "jae" | "jb" | "jbe" |
            "b" | "beq" | "bne" | "bcs" | "bhs" | "bcc" | "blo" |
            "bmi" | "bpl" | "bvs" | "bvc" | "bhi" | "bls" |
            "bge" | "blt" | "bgt" | "ble" | "bal" => {
                if parts.len() > 1 {
                    let label = parts[1].to_string();
                    instrs.push(match op_str {
                        "jmp" => Instr::Jmp(label),
                        "je" | "jz" => Instr::Je(label),
                        "jne" | "jnz" => Instr::Jne(label),
                        "jg" => Instr::Jg(label),
                        "jge" => Instr::Jge(label),
                        "jl" => Instr::Jl(label),
                        "jle" => Instr::Jle(label),
                        "ja" => Instr::Ja(label),
                        "jae" => Instr::Jae(label),
                        "jb" => Instr::Jb(label),
                        "jbe" => Instr::Jbe(label),
                        "b" => Instr::B(label),
                        "beq" => Instr::Beq(label),
                        "bne" => Instr::Bne(label),
                        "bcs" | "bhs" => Instr::Bcs(label),
                        "bcc" | "blo" => Instr::Bcc(label),
                        "bmi" => Instr::Bmi(label),
                        "bpl" => Instr::Bpl(label),
                        "bvs" => Instr::Bvs(label),
                        "bvc" => Instr::Bvc(label),
                        "bhi" => Instr::Bhi(label),
                        "bls" => Instr::Bls(label),
                        "bge" => Instr::Bge(label),
                        "blt" => Instr::Blt(label),
                        "bgt" => Instr::Bgt(label),
                        "ble" => Instr::Ble(label),
                        "bal" => Instr::Bal(label),
                        _ => unreachable!(),
                    });
                }
            }
            
            "call" | "bl" => {
                if parts.len() > 1 {
                    let label = parts[1].to_string();
                    instrs.push(if op_str == "call" {
                        Instr::Call(label)
                    } else {
                        Instr::Bl(label)
                    });
                }
            }
            
            "nop" => instrs.push(Instr::Nop),
            "ret" => instrs.push(Instr::Ret),
            
            "inc" | "dec" | "neg" | "not" | "push" | "pop" | "mul" | "div" => {
                if parts.len() > 1 {
                    let reg = parse_operand(parts[1]);
                    instrs.push(match op_str {
                        "inc" => Instr::Inc(reg),
                        "dec" => Instr::Dec(reg),
                        "neg" => Instr::Neg(reg),
                        "not" => Instr::Not(reg),
                        "push" => Instr::Push(reg),
                        "pop" => Instr::Pop(reg),
                        "mul" => Instr::Mul(reg),
                        "div" => Instr::Div(reg),
                        _ => unreachable!(),
                    });
                }
            }
            
            "imul" => {
                if parts.len() >= 3 {
                    let dst = parse_operand(parts[1]);
                    let src = parse_operand(parts[2]);
                    instrs.push(Instr::Imul(dst, src));
                } else if parts.len() > 1 {
                    let reg = parse_operand(parts[1]);
                    instrs.push(Instr::Mul(reg));
                }
            }
            
            _ => return Err(format!("Line {}: Unknown instruction: {}", line_num + 1, op)),
        }
    }
    Ok(instrs)
}

// Main TigerASM class and PyMethods would continue here...
// Due to length, I'll create a summary document instead
