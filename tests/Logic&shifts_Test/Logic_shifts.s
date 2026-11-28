@ main(void) is not used: this image enters at _start.
@ CSCE 2303 assembly template. Keep the vector table; write your program after _start.
        .syntax unified
        .cpu    cortex-m0
        .thumb

        .section .vectors, "a"
        .word   0x20040000        @ initial sp: top of RAM
        .word   _start            @ reset vector

        .text
        .thumb_func
        .global _start
_start:

    @ LSLS
    @ Input: 0x80000001

    @ Case 1: LSLS 0x80000001 << 0 = 0x80000001 with N=1, Z=0, C=Unchanged, V=Unchanged
case_1:
    movs    r3, #1
    @ C=0, V=0
    movs    r2, #0
    adds    r2, r2, #0          @ N=0, Z=1, C=0, V=0
    ldr     r0, =0x80000001
    movs    r1, #0
    lsls    r0, r0, r1
    bpl     fail_a
    beq     fail_a
    bcs     fail_a              @ C must remain 0
    bvs     fail_a              @ V must remain 0

    @ C=1, V=1
    ldr     r2, =0x80000000
    adds    r2, r2, r2          @ N=0, Z=1, C=1, V=1
    ldr     r0, =0x80000001
    movs    r1, #0
    lsls    r0, r0, r1
    bpl     fail_a
    beq     fail_a
    bcc     fail_a              @ C must remain 1
    bvc     fail_a              @ V must remain 1

    ldr     r2, =0x80000001
    cmp     r0, r2
    bne     fail_a

    @ Case 2: LSLS 0x80000001 << 32 = 0x00000000 with N=0, Z=1, C=1, V=Unchanged
case_2:
    movs    r3, #2
    movs    r2, #0
    adds    r2, r2, #0          @ C=0, V=0
    ldr     r0, =0x80000001
    movs    r1, #32
    lsls    r0, r0, r1
    bmi     fail_a
    bne     fail_a
    bcc     fail_a              @ expected C=1
    bvs     fail_a              @ V must remain 0
    cmp     r0, #0
    bne     fail_a

    @ Case 3: LSLS 0x80000001 << 33 = 0x00000000 with N=0, Z=1, C=0, V=Unchanged
case_3:
    movs    r3, #3
    ldr     r2, =0x80000000
    adds    r2, r2, r2          @ C=1, V=1
    ldr     r0, =0x80000001
    movs    r1, #33
    lsls    r0, r0, r1
    bmi     fail_a
    bne     fail_a
    bcs     fail_a              @ expected C=0
    bvc     fail_a              @ V must remain 1
    cmp     r0, #0
    bne     fail_a

    b       case_4
fail_a:
    b       fail
    .ltorg

    @ LSRS
    @ Input: 0x80000001

    @ Case 4: LSRS 0x80000001 >> 0 = 0x80000001 with N=1, Z=0, C=Unchanged, V=Unchanged
case_4:
    movs    r3, #4
    movs    r2, #0
    adds    r2, r2, #0          @ C=0, V=0
    ldr     r0, =0x80000001
    movs    r1, #0
    lsrs    r0, r0, r1
    bpl     fail_b
    beq     fail_b
    bcs     fail_b              @ C must remain 0
    bvs     fail_b              @ V must remain 0

    ldr     r2, =0x80000000
    adds    r2, r2, r2          @ C=1, V=1
    ldr     r0, =0x80000001
    movs    r1, #0
    lsrs    r0, r0, r1
    bpl     fail_b
    beq     fail_b
    bcc     fail_b              @ C must remain 1
    bvc     fail_b              @ V must remain 1

    ldr     r2, =0x80000001
    cmp     r0, r2
    bne     fail_b

    @ Case 5: LSRS 0x80000001 >> 32 = 0x00000000 with N=0, Z=1, C=1, V=Unchanged
case_5:
    movs    r3, #5
    movs    r2, #0
    adds    r2, r2, #0          @ C=0, V=0
    ldr     r0, =0x80000001
    movs    r1, #32
    lsrs    r0, r0, r1
    bmi     fail_b
    bne     fail_b
    bcc     fail_b              @ expected C=1
    bvs     fail_b              @ V must remain 0
    cmp     r0, #0
    bne     fail_b

    @ Case 6: LSRS 0x80000001 >> 33 = 0x00000000 with N=0, Z=1, C=0, V=Unchanged
case_6:
    movs    r3, #6
    ldr     r2, =0x80000000
    adds    r2, r2, r2          @ C=1, V=1
    ldr     r0, =0x80000001
    movs    r1, #33
    lsrs    r0, r0, r1
    bmi     fail_b
    bne     fail_b
    bcs     fail_b              @ expected C=0
    bvc     fail_b              @ V must remain 1
    cmp     r0, #0
    bne     fail_b

    b       case_7
fail_b:
    b       fail
    .ltorg

    @ ASRS
    @ Input: 0x80000001 

    @ Case 7: ASRS 0x80000001 >> 0 = 0x80000001 with N=1, Z=0, C=Unchanged, V=Unchanged
case_7:
    movs    r3, #7
    movs    r2, #0
    adds    r2, r2, #0          @ C=0, V=0
    ldr     r0, =0x80000001
    movs    r1, #0
    asrs    r0, r0, r1
    bpl     fail_c
    beq     fail_c
    bcs     fail_c              @ C must remain 0
    bvs     fail_c              @ V must remain 0

    ldr     r2, =0x80000000
    adds    r2, r2, r2          @ C=1, V=1
    ldr     r0, =0x80000001
    movs    r1, #0
    asrs    r0, r0, r1
    bpl     fail_c
    beq     fail_c
    bcc     fail_c              @ C must remain 1
    bvc     fail_c              @ V must remain 1

    ldr     r2, =0x80000001
    cmp     r0, r2
    bne     fail_c

    @ Case 8: ASRS 0x80000001 >> 31 = 0xFFFFFFFF with N=1, Z=0, C=0, V=Unchanged
case_8:
    movs    r3, #8
    ldr     r2, =0x80000000
    adds    r2, r2, r2          @ C=1, V=1
    ldr     r0, =0x80000001
    movs    r1, #31
    asrs    r0, r0, r1
    bpl     fail_c
    beq     fail_c
    bcs     fail_c              @ expected C=0
    bvc     fail_c              @ V must remain 1
    ldr     r2, =0xFFFFFFFF
    cmp     r0, r2
    bne     fail_c

    @ Case 9: ASRS 0x80000001 >> 32 = 0xFFFFFFFF with N=1, Z=0, C=1, V=Unchanged
case_9:
    movs    r3, #9
    movs    r2, #0
    adds    r2, r2, #0          @ C=0, V=0
    ldr     r0, =0x80000001
    movs    r1, #32
    asrs    r0, r0, r1
    bpl     fail_c
    beq     fail_c
    bcc     fail_c              @ expected C=1
    bvs     fail_c              @ V must remain 0
    ldr     r2, =0xFFFFFFFF
    cmp     r0, r2
    bne     fail_c

    @ Case 10: ASRS 0x40000000 >> 32 = 0x00000000 with N=0, Z=1, C=0, V=Unchanged
case_10:
    movs    r3, #10
    ldr     r2, =0x80000000
    adds    r2, r2, r2          @ C=1, V=1
    ldr     r0, =0x40000000
    movs    r1, #32
    asrs    r0, r0, r1
    bmi     fail_c              @ expected N=0
    bne     fail_c              @ expected Z=1
    bcs     fail_c              @ expected C=0, MSB of 0x40000000 is 0
    bvc     fail_c              @ V must remain 1
    cmp     r0, #0
    bne     fail_c

    b       case_11
fail_c:
    b       fail
    .ltorg

    @ RORS
    @ Input: 0x80000001

    @ Case 11: RORS 0x80000001 ROR 0 = 0x80000001 with N=1, Z=0, C=Unchanged, V=Unchanged
case_11:
    movs    r3, #11
    movs    r2, #0
    adds    r2, r2, #0          @ C=0, V=0
    ldr     r0, =0x80000001
    movs    r1, #0
    rors    r0, r0, r1
    bpl     fail_d
    beq     fail_d
    bcs     fail_d              @ C must remain 0
    bvs     fail_d              @ V must remain 0

    ldr     r2, =0x80000000
    adds    r2, r2, r2          @ C=1, V=1
    ldr     r0, =0x80000001
    movs    r1, #0
    rors    r0, r0, r1
    bpl     fail_d
    beq     fail_d
    bcc     fail_d              @ C must remain 1
    bvc     fail_d              @ V must remain 1

    ldr     r2, =0x80000001
    cmp     r0, r2
    bne     fail_d

    @ Case 12: RORS 0x80000001 ROR 31 = 0x00000003 with N=0, Z=0, C=0, V=Unchanged
case_12:
    movs    r3, #12
    ldr     r2, =0x80000000
    adds    r2, r2, r2          @ C=1, V=1
    ldr     r0, =0x80000001
    movs    r1, #31
    rors    r0, r0, r1
    bmi     fail_d
    beq     fail_d
    bcs     fail_d              @ expected C=0
    bvc     fail_d              @ V must remain 1
    cmp     r0, #3
    bne     fail_d

    @ Case 13: RORS 0x80000001 ROR 32 = 0x80000001 with N=1, Z=0, C=1, V=Unchanged
case_13:
    movs    r3, #13
    movs    r2, #0
    adds    r2, r2, #0          @ C=0, V=0
    ldr     r0, =0x80000001
    movs    r1, #32
    rors    r0, r0, r1
    bpl     fail_d
    beq     fail_d
    bcc     fail_d              @ expected C=1
    bvs     fail_d              @ V must remain 0
    ldr     r2, =0x80000001
    cmp     r0, r2
    bne     fail_d

    @ Case 14: 8-bit shift-amount masking 
case_14:
    movs    r3, #14
    movs    r2, #0
    adds    r2, r2, #0          @ C=0, V=0
    ldr     r0, =0x80000001
    ldr     r1, =256            @ 0x00000100, Rs low 8 bits = 0
    lsls    r0, r0, r1
    bpl     fail_d
    beq     fail_d
    bcs     fail_d              @ C must remain 0
    bvs     fail_d              @ V must remain 0
    ldr     r2, =0x80000001
    cmp     r0, r2
    bne     fail_d

    b       case_15
fail_d:
    b       fail
    .ltorg

    @ Logical instructions check N, Z; and C and V must remain unchanged

    @ Case 15: ANDS 0xFFFF0000 & 0x0000FFFF = 0x00000000 with N=0, Z=1, C=Unchanged, V=Unchanged
case_15:
    movs    r3, #15
    ldr     r2, =0x80000000
    adds    r2, r2, r2          @ C=1, V=1
    ldr     r0, =0xFFFF0000
    ldr     r1, =0x0000FFFF
    ands    r0, r0, r1
    bmi     fail_e
    bne     fail_e
    bcc     fail_e              @ C must remain 1
    bvc     fail_e              @ V must remain 1
    cmp     r0, #0
    bne     fail_e

    @ Case 16: ORRS 0xFFFF0000 | 0x0000FFFF = 0xFFFFFFFF with N=1, Z=0, C=Unchanged, V=Unchanged
case_16:
    movs    r3, #16
    movs    r2, #0
    adds    r2, r2, #0          @ C=0, V=0
    ldr     r0, =0xFFFF0000
    ldr     r1, =0x0000FFFF
    orrs    r0, r0, r1
    bpl     fail_e
    beq     fail_e
    bcs     fail_e              @ C must remain 0
    bvs     fail_e              @ V must remain 0
    ldr     r2, =0xFFFFFFFF
    cmp     r0, r2
    bne     fail_e

    @ Case 17: TST 0xFFFF0000, 0x0000FFFF = Z=1, N=0, C=Unchanged, V=Unchanged, operands intact
case_17:
    movs    r3, #17
    ldr     r2, =0x80000000
    adds    r2, r2, r2          @ C=1, V=1
    ldr     r0, =0xFFFF0000
    ldr     r1, =0x0000FFFF
    tst     r0, r1
    bmi     fail_e              @ expected N=0
    bne     fail_e              @ expected Z=1
    bcc     fail_e              @ C must remain 1
    bvc     fail_e              @ V must remain 1
    ldr     r2, =0xFFFF0000
    cmp     r0, r2
    bne     fail_e              @ r0 must not be modified
    ldr     r2, =0x0000FFFF
    cmp     r1, r2
    bne     fail_e              @ r1 must not be modified

    b       case_18
fail_e:
    b       fail
    .ltorg

    @ Extension and reversal instructions no flag change

    @ Case 18: SXTB 0x12345680 = 0xFFFFFF80
case_18:
    movs    r3, #18
    movs    r2, #0
    adds    r2, r2, #0          @ N=0, Z=1, C=0, V=0
    ldr     r1, =0x12345680
    sxtb    r0, r1
    bmi     fail_f              @ N must remain 0
    bne     fail_f              @ Z must remain 1
    bcs     fail_f              @ C must remain 0
    bvs     fail_f              @ V must remain 0
    ldr     r2, =0xFFFFFF80
    cmp     r0, r2
    bne     fail_f

    @ Case 19: SXTH 0xFFFF7FFF = 0x00007FFF
case_19:
    movs    r3, #19
    ldr     r2, =0x80000000
    adds    r2, r2, r2          @ N=0, Z=1, C=1, V=1
    ldr     r1, =0xFFFF7FFF
    sxth    r0, r1
    bmi     fail_f              @ N must remain 0
    bne     fail_f              @ Z must remain 1
    bcc     fail_f              @ C must remain 1
    bvc     fail_f              @ V must remain 1
    ldr     r2, =0x00007FFF
    cmp     r0, r2
    bne     fail_f

    @ Case 20: UXTB 0xFFFFFFFF = 0x000000FF
case_20:
    movs    r3, #20
    movs    r2, #0
    subs    r2, r2, #1          @ N=1, Z=0, C=0, V=0
    ldr     r1, =0xFFFFFFFF
    uxtb    r0, r1
    bpl     fail_f              @ N must remain 1
    beq     fail_f              @ Z must remain 0
    bcs     fail_f              @ C must remain 0
    bvs     fail_f              @ V must remain 0
    cmp     r0, #0xFF
    bne     fail_f

    @ Case 21: REV 0x12345678 = 0x78563412
case_21:
    movs    r3, #21
    movs    r2, #0
    subs    r2, r2, #1          @ N=1, Z=0, C=0, V=0
    ldr     r1, =0x12345678
    rev     r0, r1
    bpl     fail_f              @ N must remain 1
    beq     fail_f              @ Z must remain 0
    bcs     fail_f              @ C must remain 0
    bvs     fail_f              @ V must remain 0
    ldr     r2, =0x78563412
    cmp     r0, r2
    bne     fail_f

    @ Case 22: RORS 0x80000001 ROR 255 = 0x00000003 with N=0, Z=0, C=0, V=Unchanged
case_22:
    movs    r3, #24
    ldr     r2, =0x80000000
    adds    r2, r2, r2          @ C=1, V=1
    ldr     r0, =0x80000001
    movs    r1, #255
    rors    r0, r0, r1
    bmi     fail_d
    beq     fail_d
    bcs     fail_d              @ expected C=0
    bvc     fail_d              @ V must remain 1
    cmp     r0, #3
    bne     fail_d
    b       pass
fail_f:
    b       fail
    .ltorg

    @ All test cases passed & exit
pass:
    ldr     r0, =pass_msg
    svc     #0x11               @ print
    movs    r0, #0              @ Exit status = 0
    svc     #0x00

fail:
    ldr     r0, =fail_msg
    svc     #0x11               @ print
    movs    r0, r3              @ Exit status = failing case number
    svc     #0x00

        .ltorg                  @ literal pool for final ldr constants

        .section .rodata
pass_msg: .asciz "PASS\n"
fail_msg: .asciz "FAIL\n"