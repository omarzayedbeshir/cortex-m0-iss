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
        ldr     r0, =msg
        svc     #0x11             @ PUTS
        movs    r0, #0
        svc     #0x00             @ EXIT with status 0

        .ltorg                    @ literal pool for the ldr rX, =value constants

        .section .rodata
msg:    .asciz  "Hello from Thumb\n"
