@ main(void) is not used: this image enters at _start.
@ fnptr: calls through a table of function pointers with BLX
	.syntax unified
	.cpu cortex-m0
	.thumb
	.section .vectors, "a"
	.word 0x20040000
	.word _start
	.text
	.thumb_func
	.global _start
_start:
	ldr r6, =table
	movs r7, #0
1:	ldr r3, [r6, r7]
	movs r0, #10
	blx r3
	svc #0x12
	ldr r0, =32
	svc #0x10
	adds r7, #4
	cmp r7, #12
	bne 1b
	ldr r0, =10
	svc #0x10
	movs r0, #0
	svc #0x00
	.thumb_func
double:	adds r0, r0, r0
	bx lr
	.thumb_func
square:	muls r0, r0, r0
	bx lr
	.thumb_func
negate:	rsbs r0, r0, #0
	bx lr
	.ltorg
	.section .rodata
	.balign 4
table:	.word double, square, negate
