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

    @ =========================================================================
    @ Case 1: ADDS 0xFFFFFFFF + 0x00000001
    @ Expected Result : 0x00000000
    @ Expected Flags  : N=0, Z=1, C=1, V=0
    @ =========================================================================
case_1:
    movs    r3, #1              @ Set failure exit = 1

    movs    r0, #0
    mvns    r0, r0              @ r0 = 0xFFFFFFFF
    movs    r1, #1              @ r1 = 0x00000001

    adds    r0, r0, r1          @ r0 = 0x00000000, updates N, Z, C, V

    @ Verify NZCV flags
    bmi     fail                @ expected N = 0
    bne     fail                @ expected Z = 1
    bcc     fail                @ expected C = 1
    bvs     fail                @ expected V = 0

    @ Check result
    cmp     r0, #0
    bne     fail                @ branch if result != 0x00000000

    @ =========================================================================
    @ Case 2: ADDS 0x7FFFFFFF + 0x00000001
    @ Expected Result : 0x80000000
    @ Expected Flags  : N=1, Z=0, C=0, V=1
    @ =========================================================================
case_2:
    movs    r3, #2              @ Set failure exit = 2

    ldr     r0, =0x7FFFFFFF
    movs    r1, #1

    adds    r0, r0, r1          @ r0 = 0x80000000, updates N, Z, C, V

    @ Verify NZCV flags
    bpl     fail                @ expected N = 1
    beq     fail                @ expected Z = 0
    bcs     fail                @ expected C = 0
    bvc     fail                @ expected V = 1

    @ Check result
    ldr     r2, =0x80000000
    cmp     r0, r2
    bne     fail

    @ =========================================================================
    @ Case 3: ADDS 0x80000000 + 0x80000000
    @ Expected Result : 0x00000000
    @ Expected Flags  : N=0, Z=1, C=1, V=1
    @ =========================================================================
case_3:
    movs    r3, #3              @ Set failure exit = 3

    ldr     r0, =0x80000000
    ldr     r1, =0x80000000

    adds    r0, r0, r1          @ r0 = 0x00000000, updates N, Z, C, V

    @ Verify NZCV flags
    bmi     fail                @ expected N = 0
    bne     fail                @ expected Z = 1
    bcc     fail                @ expected C = 1
    bvc     fail                @ expected V = 1

    @ Check result
    cmp     r0, #0
    bne     fail

    @ =========================================================================
    @ Case 4: SUBS 0x00000000 - 0x00000001
    @ Expected Result : 0xFFFFFFFF
    @ Expected Flags  : N=1, Z=0, C=0, V=0
    @ =========================================================================
case_4:
    movs    r3, #4              @ Set failure exit = 4

    movs    r0, #0
    movs    r1, #1

    subs    r0, r0, r1          @ r0 = 0xFFFFFFFF, updates N, Z, C, V

    @ Verify NZCV flags
    bpl     fail                @ expected N = 1
    beq     fail                @ expected Z = 0
    bcs     fail                @ expected C = 0
    bvs     fail                @ expected V = 0

    @ Check result
    ldr     r2, =0xFFFFFFFF
    cmp     r0, r2
    bne     fail

    @ =========================================================================
    @ Case 5: SUBS 0x80000000 - 0x00000001
    @ Expected Result : 0x7FFFFFFF
    @ Expected Flags  : N=0, Z=0, C=1, V=1
    @ =========================================================================
case_5:
    movs    r3, #5              @ Set failure exit = 5

    ldr     r0, =0x80000000
    movs    r1, #1

    subs    r0, r0, r1          @ r0 = 0x7FFFFFFF, updates N, Z, C, V

    @ Verify NZCV flags
    bmi     fail                @ expected N = 0
    beq     fail                @ expected Z = 0
    bcc     fail                @ expected C = 1
    bvc     fail                @ expected V = 1

    @ Check result
    ldr     r2, =0x7FFFFFFF
    cmp     r0, r2
    bne     fail

    @ =========================================================================
    @ Case 6: SUBS 0x00000005 - 0x00000005
    @ Expected Result : 0x00000000
    @ Expected Flags  : N=0, Z=1, C=1, V=0
    @ =========================================================================
case_6:
    movs    r3, #6              @ Set failure exit = 6

    movs    r0, #5
    movs    r1, #5

    subs    r0, r0, r1          @ r0 = 0x00000000, updates N, Z, C, V

    @ Verify NZCV flags
    bmi     fail                @ expected N = 0
    bne     fail                @ expected Z = 1
    bcc     fail                @ expected C = 1
    bvs     fail                @ expected V = 0

    @ Check result
    cmp     r0, #0
    bne     fail

    @ =========================================================================
    @ Case 7: ADCS 0xFFFFFFFF + 0x00000000 + 1 with c=1
    @ Expected Result : 0x00000000
    @ Expected Flags  : N=0, Z=1, C=1, V=0
    @ =========================================================================
case_7:
    movs    r3, #7              @ Set failure exit = 7

    @ Pre-set Carry flag
    movs    r2, #0
    mvns    r2, r2              @ r2 = 0xFFFFFFFF
    adds    r2, r2, #1          @ set C=1

    ldr     r0, =0xFFFFFFFF
    movs    r1, #0

    adcs    r0, r0, r1          @ r0 = 0xFFFFFFFF + 0 + 1 = 0x00000000

    @ Verify NZCV flags
    bmi     fail                @ expected N = 0
    bne     fail                @ expected Z = 1
    bcc     fail                @ expected C = 1
    bvs     fail                @ expected V = 0

    @ Check result
    cmp     r0, #0
    bne     fail

    @ =========================================================================
    @ Case 8: SBCS 0x00000000 - 0x00000000 - 1 with c=0
    @ Expected Result : 0xFFFFFFFF
    @ Expected Flags  : N=1, Z=0, C=0, V=0
    @ =========================================================================
case_8:
    movs    r3, #8              @ Set failure exit = 8

    @ Pre-clear Carry flag 
    movs    r2, #0
    adds    r2, r2, #0          @ sets C=0

    movs    r0, #0
    movs    r1, #0

    sbcs    r0, r0, r1          @ r0 = 0 - 0 - ~0 = 0xFFFFFFFF

    @ Verify NZCV flags
    bpl     fail                @ expected N = 1
    beq     fail                @ expected Z = 0
    bcs     fail                @ expected C = 0
    bvs     fail                @ expected V = 0

    @ Check result
    ldr     r2, =0xFFFFFFFF
    cmp     r0, r2
    bne     fail

    @ =========================================================================
    @ Case 9: RSBS 0 - 0x80000000
    @ Expected Result : 0x80000000
    @ Expected Flags  : N=1, Z=0, C=0, V=1
    @ =========================================================================
case_9:
    movs    r3, #9              @ Set failure exit = 9

    ldr     r1, =0x80000000

    rsbs    r0, r1, #0          @ Cortex-M0 Thumb encoding: r0 = 0 - r1

    @ Verify NZCV flags
    bpl     fail                @ expected N = 1
    beq     fail                @ expected Z = 0
    bcs     fail                @ expected C = 0
    bvc     fail                @ expected V = 1

    @ Check result
    ldr     r2, =0x80000000
    cmp     r0, r2
    bne     fail

    @ =========================================================================
    @ Case 10: MULS 0x80000000 * 0x00000002
    @ Expected Result : 0x00000000
    @ Expected Flags  : N=0, Z=1, C=unmodified, V=unmodified
    @ =========================================================================
case_10:
    movs    r3, #10             @ Set failure exit = 10

    ldr     r0, =0x80000000
    movs    r1, #2

    muls    r0, r1, r0         

    @ Verify NZ flags 
    bmi     fail                @ expected N = 0
    bne     fail                @ expected Z = 1
    bcc     fail                @ expected C = 1, unmodified
    bvs     fail                @ expected V = 0, unmidified
    @ Check result
    cmp     r0, #0
    bne     fail

    @ All test cases passed
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

        .ltorg                  @ literal pool for the ldr rX, =value constants

        .section .rodata
pass_msg: .asciz "PASS\n"
fail_msg: .asciz "FAIL\n"