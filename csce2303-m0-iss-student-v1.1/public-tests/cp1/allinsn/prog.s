@ main(void) is not used: this image enters at _start.
@ allinsn: one of every encoding in the subset, for the --disasm test. Not meant to be run.
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
	movs r0, #5
	mov r8, r1
	mov r0, r9
	movs r1, r2
	mvns r0, r1
	adds r0, r1, r2
	adds r0, r1, #3
	adds r2, #200
	add r8, r0
	add r0, r8
	add r1, sp, #16
	add sp, #64
	sub sp, #64
	add r2, sp
	adr r0, data
	adcs r0, r1
	subs r0, r1, r2
	subs r0, r1, #7
	subs r3, #255
	sbcs r0, r1
	rsbs r0, r1, #0
	muls r0, r1, r0
	ands r0, r1
	orrs r0, r1
	eors r0, r1
	bics r0, r1
	tst r0, r1
	lsls r0, r1, #3
	lsls r0, r1
	lsrs r0, r1, #3
	lsrs r0, r1, #32
	lsrs r0, r1
	asrs r0, r1, #3
	asrs r0, r1, #32
	asrs r0, r1
	rors r0, r1
	cmp r0, #10
	cmp r0, r1
	cmp r8, r1
	cmn r0, r1
	sxtb r0, r1
	sxth r0, r1
	uxtb r0, r1
	uxth r0, r1
	rev r0, r1
	ldr r0, [r1, #4]
	ldr r0, [r1, r2]
	ldr r0, [sp, #8]
	ldr r0, =0x12345678
	ldrb r0, [r1, #3]
	ldrb r0, [r1, r2]
	ldrh r0, [r1, #6]
	ldrh r0, [r1, r2]
	ldrsb r0, [r1, r2]
	ldrsh r0, [r1, r2]
	str r0, [r1, #4]
	str r0, [r1, r2]
	str r0, [sp, #4]
	strb r0, [r1, #3]
	strb r0, [r1, r2]
	strh r0, [r1, #6]
	strh r0, [r1, r2]
	ldm r0!, {r1, r2}
	ldm r0, {r0, r1}
	stm r0!, {r1, r2, r3}
	push {r4, r5, r6, r7, lr}
	pop {r4, r5, r6, r7, pc}
	push {r0}
	pop {r1}
	beq 1f
	bne 1f
	bcs 1f
	bcc 1f
	bmi 1f
	bpl 1f
	bvs 1f
	bvc 1f
	bhi 1f
	bls 1f
	bge 1f
	blt 1f
	bgt 1f
	ble 1f
1:	b 2f
2:	bl func
	blx r3
	svc #0x12
	nop
	.thumb_func
func:	bx lr
	.balign 4
data:	.word 0
	.ltorg
