@ main(void) is not used: this image enters at _start.
@ CSCE 2303 assembly template. Keep the vector table; write your program after _start.
        .syntax unified
        .cpu    cortex-m0
        .thumb

        .section .vectors, "a"
        .word   0x20040000        @ initial sp: top of RAM
        .word   _start            @ reset vector

        .text
        .thumb_func
        .global _start


_start:
    @ inter first value: 
	ldr r0, =value1
	svc #0x11			@ print string
	svc #0x15			@ read int 
	movs r4, r0 		@ r4 = r0 (read integer from user )

	@ inter last value: 
	ldr r0, =value2
	svc #0x11			@ print string
	svc #0x15			@ read int 
	movs r5, r0 		@ r5 = r0 (read integer from user )

	@ inter step: 
	ldr r0, =step
	svc #0x11
	svc #0x15			@ read int 
	movs r6, r0 		@ r6 = r0 (read integer from user )
	
	movs r0, r4
	movs r1, r5
	movs r2, r6

	bl count_sum
	bl print_count_sum

    svc #0x00

.thumb_func
count_sum:
@ r2 = step, r0 = first value, r1 = last value
	sub sp, #8
	str r4, [sp, #0] 		@ store r4 in stack 
	str r5, [sp, #4]
	
	movs r4, r0 		@ put first value in r4 ,initial value for sum
	movs r5, #0		@ count = 0 
	

	cmp r2, #0		@ check step
	ble exit
loop:
	
	adds r0, r0, r2 		@ move to next value
	cmp r0, r1 		@ compare current with last
	bgt exit
	adds r5, #1	@ update count
	adds r4, r4, r0			@update sum
	b loop
exit: 

	movs r0, r4 		@ sum 
	movs r1, r5 			@ count
	ldr r4, [sp, #0] 		@ store r4 in stack 
	ldr r5, [sp, #4]
    add sp, #8

bx lr


.thumb_func
print_count_sum:

	sub sp, sp, #8         
    
    str r4, [sp, #0]      
    str r5, [sp, #4]        

    movs r4, r0             @ save sum in r4 
    movs r5, r1             @ save count in 

    ldr r0, =sum
    svc #0x11               @ print "Sum: "
    movs r0, r4             @ move sum into r0
    svc #0x12			 @ print int        

    ldr r0, =newLine
    svc #0x11               @ print "\n"

    ldr r0, =Count
    svc #0x11               @ print "Count: "
    movs r0, r5             @ move count into r0
    svc #0x12           @ print int

    ldr r0, =newLine
    svc #0x11               @ print "\n"

  	      ldr r4, [sp, #0]        
    ldr r5, [sp, #4]       
    add sp, sp, #8         @ free stack space

    bx lr                   @ return to main



	

		.section .rodata

value1: .asciz "Enter first value\n"
value2: .asciz "Enter last value\n"
step: .asciz "Enter step\n"
sum: .asciz "Sum: "
Count: .asciz "Count: "
newLine: .asciz "\n"
