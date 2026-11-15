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
        svc     #0x11             @ PUTS

        movs    r4, #0            @ uppercase count
        movs    r5, #0            @ lowercase count
        movs    r6, #0            @ digit count

        loop:   svc     #0x14             @ GETCHAR -> r0
                cmp     r0, #0
                blt     done              @ -1 = end of file
                cmp     r0, #10
                beq     done              @ newline ends the line

                cmp     r0, #'0'
                blo     loop              @ below '0': not counted
                cmp     r0, #'9'
                bls     is_digit          @ '0'..'9'
                cmp     r0, #'A'
                blo     loop              @ between '9' and 'A'
                cmp     r0, #'Z'
                bls     is_upper          @ 'A'..'Z'
                cmp     r0, #'a'
                blo     loop              @ between 'Z' and 'a'
                cmp     r0, #'z'
                bhi     loop              @ above 'z'
                adds    r5, r5, #1        @ 'a'..'z'
                b       loop

        is_digit:
                adds    r6, r6, #1
                b       loop
        is_upper:
                adds    r4, r4, #1
                b       loop

        done:   ldr     r0, =msg_upper
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
prompt:    .asciz  "Enter a string: "
msg_upper:      .asciz "Uppercase letters: "
msg_lower:      .asciz "Lowercase letters: "
msg_digits:     .asciz "Digits: "
newline:        .asciz "\n"
