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
        ldr     r0, =prompt
        svc     #0x11             @ PUTS prompt
        sub     sp, #256          @ input buffer

        movs    r4, #0            @ uppercase count
        movs    r5, #0            @ lowercase count
        movs    r6, #0            @ digit count

        movs    r0, #0            @ stdin
        mov     r1, sp            @ buffer address
        movs    r2, #255          @ max bytes
        svc     #0x22             @ READ -> byte count in r0
        movs    r3, r0            @ bytes left (0 if empty input)
        mov     r7, sp            @ next byte

loop:   cmp     r3, #0
        beq     done
        ldrb    r0, [r7]
        adds    r7, #1
        subs    r3, #1
        cmp     r0, #10
        beq     done              @ newline, end of string

        movs    r1, r0
        subs    r1, #'0'
        cmp     r1, #9
        bls     is_digit

        movs    r1, r0
        subs    r1, #'A'
        cmp     r1, #25
        bls     is_upper

        movs    r1, r0
        subs    r1, #'a'
        cmp     r1, #25
        bhi     loop              @ not a letter
        adds    r5, #1            @ lowercase
        b       loop

is_digit:
        adds    r6, #1
        b       loop
is_upper:
        adds    r4, #1
        b       loop

done:   add     sp, #256          @ free the buffer

        ldr     r0, =msg_upper
        svc     #0x11
        movs    r0, r4
        svc     #0x12             @ PUTINT
        ldr     r0, =newline
        svc     #0x11

        ldr     r0, =msg_lower
        svc     #0x11
        movs    r0, r5
        svc     #0x12
        ldr     r0, =newline
        svc     #0x11

        ldr     r0, =msg_digits
        svc     #0x11
        movs    r0, r6
        svc     #0x12
        ldr     r0, =newline
        svc     #0x11

        movs    r0, #0
        svc     #0x00             @ EXIT with status 0

        .ltorg                    @ literal pool for the ldr rX, =value constants

        .section .rodata
prompt:     .asciz "Enter a string: "
msg_upper:  .asciz "Uppercase letters: "
msg_lower:  .asciz "Lowercase letters: "
msg_digits: .asciz "Digits: "
newline:    .asciz "\n"