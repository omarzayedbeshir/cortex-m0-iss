@ main(void) is not used: this image enters at _start.
@ factorial: prints "10! = 3628800" and exits with status 0
        .syntax unified
        .cpu cortex-m0
        .thumb
        .section .vectors,"a"
        .word 0x20040000          @ initial SP
        .word _start              @ reset vector (Thumb bit set by assembler for thumb_func)
        .text
        .thumb_func
        .global _start
_start: ldr  r0, =msg
        svc  #0x11                @ PUTS
        movs r0, #10
        bl   fact
        svc  #0x12                @ PUTINT
        movs r0, #0
        svc  #0x00                @ EXIT
        .thumb_func
fact:   push {r4, lr}             @ recursive factorial
        movs r4, r0
        cmp  r0, #1
        ble  1f
        subs r0, #1
        bl   fact
        muls r0, r4, r0
        pop  {r4, pc}
1:      movs r0, #1
        pop  {r4, pc}
        .section .rodata
msg:    .asciz "10! = "
