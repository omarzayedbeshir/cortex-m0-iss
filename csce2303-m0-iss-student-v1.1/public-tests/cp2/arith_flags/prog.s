@ main(void) is not used: this image enters at _start.
@ arith_flags: results and flags of the arithmetic, logic and shift instructions
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
	ldr r1, =0xFFFFFFFF
	movs r2, #1
	adds r0, r1, r2          @ 0, carry out
	bl phex
	bl pflags
	ldr r1, =0x7FFFFFFF
	adds r0, r1, r2          @ signed overflow
	bl phex
	bl pflags
	movs r1, #3
	movs r2, #5
	subs r0, r1, r2          @ borrow: C clear
	bl phex
	bl pflags
	subs r0, r2, r1          @ no borrow: C set
	bl phex
	bl pflags
	ldr r4, =0xFFFFFFFF      @ 64-bit add: (1:FFFFFFFF) + (0:00000001)
	movs r5, #1
	movs r6, #1
	movs r7, #0
	adds r0, r4, r6
	mov r1, r5
	adcs r1, r7
	bl phex
	mov r0, r1
	bl phex
	bl pflags
	movs r0, #0              @ sbcs after a compare
	movs r1, #1
	cmp r1, r0
	movs r3, #10
	sbcs r3, r1
	mov r0, r3
	bl phex
	bl pflags
	movs r1, #7
	rsbs r0, r1, #0
	bl phex
	bl pflags
	ldr r0, =100000
	ldr r1, =3000
	muls r0, r1, r0
	bl phex
	bl pflags
	ldr r0, =0xF0F0F0F0
	ldr r1, =0x0FF00FF0
	mov r2, r0
	ands r2, r1
	mov r0, r2
	bl phex
	ldr r0, =0xF0F0F0F0
	orrs r0, r1
	bl phex
	ldr r0, =0xF0F0F0F0
	eors r0, r1
	bl phex
	ldr r0, =0xF0F0F0F0
	bics r0, r1
	bl phex
	mvns r0, r1
	bl phex
	bl pflags
	ldr r1, =0x80000001      @ shifts by immediate
	lsls r0, r1, #1
	bl phex
	bl pflags
	lsrs r0, r1, #1
	bl phex
	bl pflags
	asrs r0, r1, #4
	bl phex
	bl pflags
	lsrs r0, r1, #32
	bl phex
	bl pflags
	asrs r0, r1, #32
	bl phex
	bl pflags
	ldr r4, =0
	ldr r5, =32
	ldr r6, =33
	ldr r7, =255
	mov r0, r1               @ shifts by register: 0, 32, 33, 255
	lsls r0, r4
	bl phex
	bl pflags
	mov r0, r1
	lsls r0, r5
	bl phex
	bl pflags
	mov r0, r1
	lsls r0, r6
	bl phex
	bl pflags
	mov r0, r1
	lsrs r0, r5
	bl phex
	bl pflags
	mov r0, r1
	asrs r0, r7
	bl phex
	bl pflags
	ldr r2, =4
	mov r0, r1
	rors r0, r2
	bl phex
	bl pflags
	mov r0, r1
	rors r0, r5
	bl phex
	bl pflags
	mov r0, r1
	tst r0, r4
	bl pflags
	cmn r1, r1
	bl pflags
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
