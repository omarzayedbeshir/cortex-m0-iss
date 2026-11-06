@ main(void) is not used: this image enters at _start.
@ multiple: LDM, STM and multi-register PUSH and POP, including the writeback rules
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
	ldr r0, =src             @ copy 8 words with LDM/STM, four at a time
	ldr r5, =dst
	movs r6, #2
1:	ldm r0!, {r1, r2, r3, r4}
	stm r5!, {r1, r2, r3, r4}
	subs r6, #1
	bne 1b
	ldr r1, =dst
	subs r0, r5, r1          @ bytes advanced by the STM writeback: 32
	svc #0x12
	ldr r0, =10
	svc #0x10
	ldr r6, =dst             @ print the copy
	movs r7, #0
2:	ldr r0, [r6, r7]
	bl phex
	adds r7, #4
	cmp r7, #32
	bne 2b
	ldr r0, =10
	svc #0x10
	ldr r0, =dst             @ LDM with the base in the list: no writeback
	ldm r0, {r0, r1}
	bl phex
	mov r0, r1
	bl phex
	ldr r0, =10
	svc #0x10
	movs r1, #1              @ PUSH and POP many registers, in order
	movs r2, #2
	movs r3, #3
	movs r4, #4
	push {r1, r2, r3, r4}
	pop {r4}
	pop {r1, r2, r3}
	mov r0, r4
	bl phex
	mov r0, r1
	bl phex
	mov r0, r3
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
	.balign 4
src:	.word 0x11111111, 0x22222222, 0x33333333, 0x44444444, 0x55555555, 0x66666666, 0x77777777, 0x88888888
	.data
	.balign 4
dst:	.space 32
