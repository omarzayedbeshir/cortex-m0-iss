@ main(void) is not used: this image enters at _start.
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
	ldr r0, =0x200
	bx r0
	movs r0, #0
	svc #0x00
	.ltorg
