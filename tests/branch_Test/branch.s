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

    @ Conditional Branches
   
    @ Case 1: Equal operands
    @CMP 5, 5 --> N=0, Z=1, C=1, V=0
    @ Taken     : BEQ, BCS, BPL, BVC, BLS, BGE, BLE
    @ Not taken : BNE, BCC, BMI, BVS, BHI, BLT, BGT
case_1:
    movs    r3, #1              @ Set failure exit = 1
    movs    r0, #5
    movs    r1, #5
    cmp     r0, r1              @ N=0, Z=1, C=1, V=0

    @ Not-taken checks
    bne     fail_a
    bcc     fail_a
    bmi     fail_a
    bvs     fail_a
    bhi     fail_a
    blt     fail_a
    bgt     fail_a

    @ Taken checks 
    beq     c1_t1
    b       fail_a
c1_t1:
    bcs     c1_t2
    b       fail_a
c1_t2:
    bpl     c1_t3
    b       fail_a
c1_t3:
    bvc     c1_t4
    b       fail_a
c1_t4:
    bls     c1_t5
    b       fail_a
c1_t5:
    bge     c1_t6
    b       fail_a
c1_t6:
    ble     case_2
    b       fail_a

    @ Case 2: Positive result 
    @CMP 5, 3 --> N=0, Z=0, C=1, V=0
    @ Taken     : BNE, BCS, BPL, BVC, BHI, BGE, BGT
    @ Not taken : BEQ, BCC, BMI, BVS, BLS, BLT, BLE
case_2:
    movs    r3, #2              @ Set failure exit = 2
    movs    r0, #5
    movs    r1, #3
    cmp     r0, r1              @ N=0, Z=0, C=1, V=0

    @ Not-taken checks
    beq     fail_a
    bcc     fail_a
    bmi     fail_a
    bvs     fail_a
    bls     fail_a
    blt     fail_a
    ble     fail_a

    @ Taken checks
    bne     c2_t1
    b       fail_a
c2_t1:
    bcs     c2_t2
    b       fail_a
c2_t2:
    bpl     c2_t3
    b       fail_a
c2_t3:
    bvc     c2_t4
    b       fail_a
c2_t4:
    bhi     c2_t5
    b       fail_a
c2_t5:
    bge     c2_t6
    b       fail_a
c2_t6:
    bgt     case_3
    b       fail_a

    @ Case 3: Negative result
    @CMP 3, 5 -> N=1, Z=0, C=0, V=0
    @ Taken     : BNE, BCC, BMI, BVC, BLS, BLT, BLE
    @ Not taken : BEQ, BCS, BPL, BVS, BHI, BGE, BGT
case_3:
    movs    r3, #3              @ Set failure exit = 3
    movs    r0, #3
    movs    r1, #5
    cmp     r0, r1              @ N=1, Z=0, C=0, V=0

    @ Not-taken checks
    beq     fail_a
    bcs     fail_a
    bpl     fail_a
    bvs     fail_a
    bhi     fail_a
    bge     fail_a
    bgt     fail_a

    @ Taken checks
    bne     c3_t1
    b       fail_a
c3_t1:
    bcc     c3_t2
    b       fail_a
c3_t2:
    bmi     c3_t3
    b       fail_a
c3_t3:
    bvc     c3_t4
    b       fail_a
c3_t4:
    bls     c3_t5
    b       fail_a
c3_t5:
    blt     c3_t6
    b       fail_a
c3_t6:
    ble     case_4
    b       fail_a

    b       case_4
fail_a:
    b       fail               
    .ltorg

    @ Case 4: Signed overflow 
    @ADDS 0x7FFFFFFF + 1 --> N=1, Z=0, C=0, V=1
    @ Taken     : BNE, BCC, BMI, BVS, BLS, BGE, BGT
    @ Not taken : BEQ, BCS, BPL, BVC, BHI, BLT, BLE
case_4:
    movs    r3, #4              @ Set failure exit = 4
    ldr     r0, =0x7FFFFFFF
    movs    r1, #1
    adds    r0, r0, r1          @ r0 = 0x80000000 with N=1, Z=0, C=0, V=1

    @ Not-taken checks
    beq     fail_b
    bcs     fail_b
    bpl     fail_b
    bvc     fail_b
    bhi     fail_b
    blt     fail_b
    ble     fail_b

    @ Taken checks
    bne     c4_t1
    b       fail_b
c4_t1:
    bcc     c4_t2
    b       fail_b
c4_t2:
    bmi     c4_t3
    b       fail_b
c4_t3:
    bvs     c4_t4
    b       fail_b
c4_t4:
    bls     c4_t5
    b       fail_b
c4_t5:
    bge     c4_t6
    b       fail_b
c4_t6:
    bgt     case_5
    b       fail_b

    @  Branch Offsets & Flag Preservation

    @ Case 5: Forward unconditional B 
case_5:
    movs    r3, #5              @ Set failure exit = 5
    movs    r0, #0
    b       c5_target
    movs    r0, #99             @ must be skiped
    b       fail_b              @ must be skiped
c5_target:
    cmp     r0, #0
    bne     fail_b

    @ Case 6: Backward conditional B 
case_6:
    movs    r3, #6              @ Set failure exit = 6
    movs    r0, #0              @  counter
    movs    r1, #5              @ Target  count
c6_loop:
    adds    r0, r0, #1          @ r0 = 1, 2, 3, 4, 5
    cmp     r0, r1
    blt     c6_loop             @ Backward conditional branch when r0 < 5
    cmp     r0, #5
    bne     fail_b

    @ Case 7: Taken branch targeting the next instruction
case_7:
    movs    r3, #7              @ Set failure exit = 7
    movs    r0, #1
    cmp     r0, #1              @ Z=1
    beq     c7_next             @ Taken conditional branch 
c7_next:
    b       c7_next2            @ Taken unconditional branch 
c7_next2:
    movs    r0, #42
    cmp     r0, #42
    bne     fail_b

    @ Case 8: Unconditional B with established flags 
case_8:
    movs    r3, #8              @ Set failure exit = 8

    @ Test preservation of N=1, Z=0, C=0, V=1
    ldr     r0, =0x7FFFFFFF
    movs    r1, #1
    adds    r0, r0, r1          @ N=1, Z=0, C=0, V=1
    b       c8_check1
    b       fail_b
c8_check1:
    bpl     fail_b              @ N must remain 1
    beq     fail_b              @ Z must remain 0
    bcs     fail_b              @ C must remain 0
    bvc     fail_b              @ V must remain 1

    @ Test preservation of N=0, Z=1, C=1, V=0
    movs    r0, #5
    cmp     r0, #5              @ N=0, Z=1, C=1, V=0
    b       c8_check2
    b       fail_b
c8_check2:
    bmi     fail_b              @ N must remain 0
    bne     fail_b              @ Z must remain 1
    bcc     fail_b              @ C must remain 1
    bvs     fail_b              @ V must remain 0

    b       pass
fail_b:
    b       fail

    @ All test cases passed / Common Exit Handlers
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