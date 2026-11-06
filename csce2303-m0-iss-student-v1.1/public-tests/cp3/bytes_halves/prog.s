@ main(void) is not used: this image enters at _start.
@ bytes_halves: byte, halfword and signed loads and stores
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
	ldr r0, =buf             @ reverse a string in place with LDRB/STRB
	ldr r1, =text
	movs r2, #0
1:	ldrb r3, [r1, r2]
	strb r3, [r0, r2]
	adds r2, #1
	cmp r3, #0
	bne 1b
	subs r2, #2              @ r2 = index of the last character
	movs r1, #0
2:	cmp r1, r2
	bge 3f
	ldrb r3, [r0, r1]
	ldrb r4, [r0, r2]
	strb r4, [r0, r1]
	strb r3, [r0, r2]
	adds r1, #1
	subs r2, #1
	b 2b
3:	svc #0x11
	ldr r0, =10
	svc #0x10
	ldr r6, =halves          @ halfwords, unsigned and signed
	ldrh r0, [r6, #0]
	bl phex
	ldrh r0, [r6, #2]
	bl phex
	movs r7, #2
	ldrsh r0, [r6, r7]
	bl phex
	ldr r6, =bytes
	movs r7, #1
	ldrb r0, [r6, r7]
	bl phex
	ldrsb r0, [r6, r7]
	bl phex
	ldr r0, =10
	svc #0x10
	ldr r6, =hbuf            @ store halfwords and bytes, read back a word
	ldr r0, =0xBEEF
	strh r0, [r6, #0]
	ldr r0, =0x1234
	movs r7, #2
	strh r0, [r6, r7]
	ldr r0, [r6, #0]
	bl phex
	movs r0, #0xAB
	strb r0, [r6, #1]
	ldr r0, [r6, #0]
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
	.section .rodata
text:	.asciz "Thumb is not RISC-V"
	.balign 2
halves:	.hword 0x1234, 0x8001
bytes:	.byte 0x7F, 0x80
	.data
	.balign 4
buf:	.space 32
hbuf:	.space 8
