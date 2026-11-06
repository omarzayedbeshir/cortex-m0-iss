@ main(void) is not used: this image enters at _start.
	.syntax unified
	.cpu cortex-m0
	.thumb
	.section .vectors, "a"
	.word 0x20040000
	.word 0x00000100
	.text
	movs r0, #0
	svc #0x00
