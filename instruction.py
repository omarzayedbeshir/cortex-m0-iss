from typing import Optional
from enum import Enum
from dataclasses import dataclass




        

class Op(str, Enum):

    MOV = "MOV"         # MOVS #imm8, MOV reg, MOVS reg (LSLS #0)
    MVN = "MVN"         # MVNS Rd, Rm

    # Arithmetic
    ADD = "ADD"         # ADDS imm3/imm8/reg, ADD high/SP+reg/SP+imm7/SP+imm8
    ADR = "ADR"         # ADR Rd, label (Align(PC + 4, 4) + imm32)
    ADC = "ADC"         # ADCS Rdn, Rm
    SUB = "SUB"         # SUBS imm3/imm8/reg, SUB SP-imm7
    SBC = "SBC"         # SBCS Rdn, Rm
    RSB = "RSB"         # RSBS Rd, Rn, #0
    MUL = "MUL"         # MULS Rdm, Rn, Rdm

    # Logic & Shifts
    AND = "AND"         # ANDS Rdn, Rm
    ORR = "ORR"         # ORRS Rdn, Rm
    EOR = "EOR"         # EORS Rdn, Rm
    BIC = "BIC"         # BICS Rdn, Rm
    TST = "TST"         # TST Rn, Rm
    LSL = "LSL"         # LSLS imm5, LSLS reg
    LSR = "LSR"         # LSRS imm5, LSRS reg
    ASR = "ASR"         # ASRS imm5, ASRS reg
    ROR = "ROR"         # RORS Rdn, Rm

    # Compare
    CMP = "CMP"         # CMP #imm8, CMP reg (low & high)
    CMN = "CMN"         # CMN Rn, Rm

    # Extend & Reverse
    SXTB = "SXTB"       # SXTB Rd, Rm
    SXTH = "SXTH"       # SXTH Rd, Rm
    UXTB = "UXTB"       # UXTB Rd, Rm
    UXTH = "UXTH"       # UXTH Rd, Rm
    REV = "REV"         # REV Rd, Rm

    # Load & Store
    LDR = "LDR"         # LDR imm5, LDR [SP, #imm8], LDR reg, LDR literal [PC, #imm8]
    LDRB = "LDRB"       # LDRB imm5, LDRB reg
    LDRH = "LDRH"       # LDRH imm5, LDRH reg
    LDRSB = "LDRSB"     # LDRSB reg
    LDRSH = "LDRSH"     # LDRSH reg
    STR = "STR"         # STR imm5, STR [SP, #imm8], STR reg
    STRB = "STRB"       # STRB imm5, STRB reg
    STRH = "STRH"       # STRH imm5, STRH reg

    # Multiple
    LDM = "LDM"         # LDM Rn{!}, <registers>
    STM = "STM"         # STM Rn!, <registers>
    PUSH = "PUSH"       # PUSH <registers>
    POP = "POP"         # POP <registers>

    # Control & System
    B = "B"             # B label (condition=None) and B<c> label (condition=0..13)
    BL = "BL"           # BL label (32-bit, size=4)
    BX = "BX"           # BX Rm
    BLX = "BLX"         # BLX Rm
    SVC = "SVC"         # SVC #imm8

            # NOP
    NOP = "NOP"         

@dataclass
class INSTRUCTION:
    op: Op                      # Unique operation name (e.g., "ADDS", "LDR"...)
    rd: Optional[int] = None         # Destination register (0..15)
    rs1: Optional[int] = None         # First source / base register (0..15)
    rs2: Optional[int] = None         # Second source / offset register (0..15)
    rt: Optional[int] = None         # Target register for LDR/STR (0..15)
    n: Optional[int] = None         # for service calls 
    imm32: Optional[int] = None      # Decoded (sign- or zero-extended) immediate
    isImm: bool = False
    isImm3: bool = False            # this will be used to distinguish ADD/SUB syntax of imm3, imm8 (imm3 always have two regs even they are equal)
    condition: Optional[int] = None       # 4-bit condition code for B<c>
    branch_taken: bool = False            #flag Whether branch taken 
    memory_accesses: int = 0              #
    registers: Optional[int] = None  # 16-bit register bitmask for LDM/STM/PUSH/POP
    write_back: bool = False              # Write-back flag for LDM/STM/PUSH/POP
    index: bool = True 
    add: bool = True 


    # True if instruction updates APSR flags
    setflags: bool = False 


          
