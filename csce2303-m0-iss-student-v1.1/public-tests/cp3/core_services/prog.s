@ main(void) is not used: this image enters at _start.
@ core_services: READ, WRITE, INSTRET and DUMP_REGS
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
	ldr r1, =buf
	movs r0, #0
	movs r2, #64
	svc #0x22                @ READ up to 64 bytes of stdin
	mov r4, r0
	svc #0x12                @ bytes read
	ldr r0, =10
	svc #0x10
	movs r0, #1
	ldr r1, =buf
	mov r2, r4
	svc #0x23                @ WRITE them back to stdout
	movs r0, #1
	ldr r1, =buf
	movs r2, #0
	svc #0x22                @ READ from fd 1: -9
	svc #0x12
	ldr r0, =10
	svc #0x10
	movs r0, #0
	ldr r1, =buf
	movs r2, #8
	svc #0x22                @ READ at end of file: 0
	svc #0x12
	ldr r0, =10
	svc #0x10
	svc #0x30                @ INSTRET
	svc #0x12
	ldr r0, =10
	svc #0x10
	svc #0x40                @ DUMP_REGS goes to stderr, in a format you choose
	movs r0, #0
	svc #0x00
	.ltorg
	.data
buf:	.space 64
