@ main(void) is not used: this image enters at _start.
@ services: exercises every Core and Extended service once
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
	movs r0, #'A'
	svc #0x10              @ PUTCHAR 'A'
	movs r0, #10
	svc #0x10
	ldr r0, =msg
	svc #0x11              @ PUTS
	ldr r0, =-123456
	svc #0x12              @ PUTINT -123456
	movs r0, #10
	svc #0x10
	ldr r0, =0xdeadbeef
	svc #0x13              @ PUTHEX 0xDEADBEEF
	movs r0, #10
	svc #0x10
	svc #0x15              @ GETINT  (input "  -42 x\n")
	svc #0x12
	movs r0, #10
	svc #0x10
	svc #0x15              @ GETINT with no number -> 0
	svc #0x12
	movs r0, #10
	svc #0x10
	svc #0x14              @ GETCHAR -> 'x' (120): the failed GETINT consumed the spaces
	svc #0x12
	movs r0, #10
	svc #0x10
	ldr r1, =buf
	movs r0, #0
	movs r2, #16
	svc #0x22              @ READ the rest of stdin ("\n") -> 1
	svc #0x12
	movs r0, #10
	svc #0x10
	svc #0x14              @ GETCHAR at end of file -> -1
	svc #0x12
	movs r0, #10
	svc #0x10
	movs r0, #1
	ldr r1, =buf
	movs r2, #2
	svc #0x23              @ WRITE 2 bytes of buf ("\n", NUL) to stdout
	movs r0, #5
	ldr r1, =buf
	movs r2, #1
	svc #0x23              @ WRITE to fd 5 -> -9
	svc #0x12
	movs r0, #10
	svc #0x10
	svc #0x32              @ RAND x3
	svc #0x13
	svc #0x32
	svc #0x13
	svc #0x32
	svc #0x13
	movs r0, #10
	svc #0x10
	svc #0x30              @ INSTRET
	svc #0x12
	movs r0, #10
	svc #0x10
	ldr r0, =buf
	movs r1, #4
	svc #0x41              @ DUMP_MEM (stderr)
	svc #0x40              @ DUMP_REGS (stderr)
	movs r0, #3
	svc #0x00              @ EXIT 3
	.ltorg
	.section .rodata
msg:	.asciz "hello, services\n"
	.data
buf:	.space 16
