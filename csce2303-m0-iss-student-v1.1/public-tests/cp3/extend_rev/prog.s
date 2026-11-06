@ main(void) is not used: this image enters at _start.
@ extend_rev: SXTB, SXTH, UXTB, UXTH and REV
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
	ldr r1, =0x1234F68A
	sxtb r0, r1
	bl phex
	sxth r0, r1
	bl phex
	uxtb r0, r1
	bl phex
	uxth r0, r1
	bl phex
	rev r0, r1
	bl phex
	ldr r0, =10
	svc #0x10
	ldr r1, =0x00007F7F
	sxtb r0, r1
	bl phex
	sxth r0, r1
	bl phex
	ldr r0, =10
	svc #0x10
	movs r0, #0
	svc #0x00

@ pflags: print the flags as letters (N Z C V), then a newline. Changes no flags.
	.thumb_func
pflags:	push {r0, lr}
	bpl 1f
	ldr r0, =78
	svc #0x10
1:	bne 2f
	ldr r0, =90
	svc #0x10
2:	bcc 3f
	ldr r0, =67
	svc #0x10
3:	bvc 4f
	ldr r0, =86
	svc #0x10
4:	ldr r0, =10
	svc #0x10
	pop {r0, pc}
@ phex: print r0 as hex and a space. Changes no flags.
	.thumb_func
phex:	push {r0, lr}
	svc #0x13
	ldr r0, =32
	svc #0x10
	pop {r0, pc}
	.ltorg
