@DONE BY YOUSEF OMAR 
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

	LDR R0, =numElement_Msg	@get address of msg in R0
	SVC #0x11
	
	@ Read array size n 
    SVC  #0x15
    MOVS R4, R0
	
	@check for negative size
	CMP R4, #0
	BLE exit	
	
	@------------ allocate memory -------------
	LSLS R5, R4, #2             @ R5 = n << 2 
    ADDS R5, #7                 @ Add 7
    LSRS R5, R5, #3             @ Divide by 8 
    LSLS R5, R5, #3             @ Multiply by 8 
	
	MOV R0, SP 	@pointer to stack
	SUBS R0, R0, R5	@Free stack for the array
	MOV SP, R0 
	MOVS R6, R0 	@6 base address
	@------------- call read array ------------
	@R0, base address, R1 size of the array
	MOVS R0, R6
	MOVS R1, R4 
	BL readArray
	
	@--------------call sum --------------
	MOVS R0, R6
	MOVS R1, R4
	BL sum 
	MOVS R7, R0 	@SUM IN R3
	@-------------- call max_min --------------
	MOVS R0, R6
	MOVS R1, R4
	BL max_min 
	MOVS R4, R0	@MAX, over write R4
	MOVS R6, R1 @MIN, over write R6 
	
	@call print 
	MOVS R0, R7 @SUM 
	MOVS R1, R4 @max
	MOVS R2, R6 @MIN 

	BL print_result
	
	@Reset stack
	MOV R0, SP
	ADDS R0, R0, R5
	MOV SP, R0

exit:						
    MOVS R0, #0                 @ Return 0 
    SVC  #0x00
	
.thumb_func 
print_result: 
	PUSH {R4, R5, R6, LR}
	
	MOVS R4, R0
	MOVS R5, R1
	MOVS R6, R2 

	LDR R0, =sumMsg
	SVC #0x11 
	MOVS R0, R4 
	SVC #0x12 
	LDR R0, =newLine 
	SVC #0x11  
	
	LDR R0, =maxMsg
	SVC #0x11 
	MOVS R0, R5 
	SVC #0x12 
	LDR R0, =newLine 
	SVC #0x11  
	
	LDR R0, =minMsg
	SVC #0x11 
	MOVS R0, R6 
	SVC #0x12 
	LDR R0, =newLine 
	SVC #0x11  
	
	POP {R4, R5, R6, PC }
	
	
	
.thumb_func
readArray:
	PUSH {R4, R5, R6, LR} @Push to stack 
	MOV R4, R0	@base address 
	MOV R5, R1	@size
	
Loop:
	@if R5 <= 0
	CMP R5, #0
	BLE Exit_loop
	
	
	@read element
	SVC #0x15 
	STR R0, [R4, #0]
	
	ADDS R4, #4	@update the address for next element
	SUBS R5, #1
	
	B Loop 	@repeat
	
Exit_loop:	
	POP {R4, R5, R6, PC}
	
	
	
.thumb_func
sum: 
	PUSH {R4, R5, R6, LR }
	MOVS R4, R0 @base address
	MOVS R5, R1 @n size 
	MOVS R6, #0	@sum = 0 at first
	
loop: 
	CMP R5, #0
	BLE Exit_loop1
	
	LDR R0, [R4, #0] 	@load value from the current i 
	ADDS R6, R6, R0 	@SUM = SUM + ARR[i]
	
	SUBS R5, #1 @n-=1
	ADDS R4, #4 @move to next element
	
	B loop @repeat
	
	
Exit_loop1:
	MOVS R0, R6
	POP {R4, R5, R6, PC}
	
	
.thumb_func
max_min: 
	PUSH {R3,R4, R5, R6}
	MOVS R3,R0 @base address
	MOVS R4, R1 @size
	
	LDR R5, [R3, #0]	@Assume first leement is max
	MOVS R6, R5 		@ASSUME first element is min
	
	ADDS R3, #4 			@MOVE TO NEXT ELEMENT
	SUBS R4, #1
	
loop2: 
	CMP R4, #0
	BLE Exit_loop2
	
	LDR R0, [R3, #0]
	 		 
	
	ADDS R3, #4 			@MOVE TO NEXT ELEMENT
	SUBS R4, #1
	
	CMP R0, R5
	BGT max 	@arr[i]> max
	
	CMP R0, R6 
	BLE min 	@arr[i]< min
	
	B loop2 @repeat
max: 
	MOVS R5, R0 
	B loop2 
min:	
	MOVS R6, R0 
	B loop2
	
Exit_loop2:
	MOVS R0, R5 
	MOVS R1, R6
	POP {R3,R4, R5, R6}	
	BX LR 
	

.ltorg

.section .rodata
numElement_Msg: .asciz "Enter the number of Element:\n"
sumMsg:         .asciz "sum is: "
maxMsg:         .asciz "max is: "
minMsg:         .asciz "min is: "
newLine: 		.asciz "\n"	