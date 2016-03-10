# RISC521 Assembler -- User's Guide
by Connor Goldberg

## Introduction

This assembler is specifically designed for the RISC521 design.
The specifications for my design are as follows:

 - Von Neumann
 - 12 bit register size

## Installation

To install, just download all python files into the same directory. This 
assumes that Python 2.7 is already installed.

## Execution

Open either a command prompt (windows) or a terminal (Mac / Linux). Change
directory into the directory where the python files were downloaded. To run, 
type the following command:

`python Assembler.py [-h] assembly-file [-o out-file] [-d depth] [-w width]`

Alternatively, Mac and Linux users can execute the assembler by using the
the following (assuming that you are in the same directory):

`./Assembler.py [-h] assembly-file [-o out-file] [-d depth] [-w width]`

By default, the output file takes the name of the input file, but replacing the
original file extension with ".mif". The name of the output file can be overridden
by using the -o or --output option in the command line. Example:

`python Assembler.py cjg.asm -o cjg_new.mif`

This command will take the assembly code in "cjg.asm" and put the machine code in
the file named "cjg_new.mif". Note, if a name is manually entered that does not have
the ".mif" file extension, it will be added automatically. Below are all options.
The depth and width modify options of the assembled file.

`-h or --help, -o or --output, -d or --depth, -w or --width`

## Assembly Language

The assembly language currently has support for code, directives, and constants. 

### Directives

This section is started by the identifier of '.directives' and ends with the line: '.enddirectives'.
Within this section it is possible to create pre-processor like definitions for variables. These
variables are never seen in the actual machine code, they are replaced by the assembler by their actual
values before the code is assembled.

To use these directives later on in the code, the variables are referenced by the '$' symbol.

Example: 

```
.directives
	foo		0x001;
	bar		0x002;
.enddirectives

.code
	ADDC R1, $foo;
	SUBC R2, $bar;
.endcode
```


### Constants

This section is started by the identifier of '.constants' and ends with the line: '.endconstants'.
This section contains values that will be placed into memory. The first value per line is the destination
address of the value, and the second contains the actual value that will be initialized at that memory location.


Example: 

```
.constants
	0x100 0x001;
	0x200 0x002;
.endconstants
```

### Code

This is denoted by the .code and .endcode keywords. In this section, the instructions are decoded to machine code.

Each instruction line ends with a semicolon, and comments are denoted by "//".

Each actual instruction will be preserved and put in the machine code as a comment for each line for reference.

### Types of Instructions

There are 3 main types of instructions: data transfer, manipulation, and flow control. 
Data transfer instructions are responsible for moving data to different registers or memory locations, but 
they do not change the data. Flow control instructions are responsible for moving forward or backward in 
the program depending on certain conditions. Manipulation instructions do not move data, however they change
data in registers. However, these types of instructions are not all the same in terms of the operands 
that they accept. 

The following expands on the different types of instructions by operand.

#### -Register

These instructions perform an operation on a single register.

> NOT

 Example: `NOT R1;`

This instruction performs a bitwise NOT on R1.

#### -Register, Register

For these instructions, the destination operand is first, followed by the source operand.

> CPY, SWAP, ADD, SUB, AND, OR

Example: `ADD Ri, Rj;`

This instruction takes the value of R1, adds R2, and stores the result back into R1.

#### -Register, Constant

These instructions perform an operation on the destination (first) operand using a constant value
provided in the instruction word.

> ADDC, SUBC, SHRA, ROTR

Example: `ADDC Ri, 0x2;`

This instruction takes the value of R1, and adds 0x1 to it.

#### -Register, Memory

These instructions used load and store information using the memory.

> LD, ST

Example: `LD Rj, M[Ri, 0x1];`

This instruction takes the word that is located at the value of R1 + 0x1, and stores it in R2.

Example: `ST M[Rj, 0x0], Ri;`

This instruction places the value that is located in R2 into memory at the address of R1.

#### -Memory

These instructions are the jump / flow control instructions. Depending on the mnemonic, the
program will jump to a different value in memory.

> JU, JC, JNC, JN, JNN, JV, JNV, JZ, JNZ

The JMP instruction is the unconditional jump. The others take use the status register.
The carry (C), negative (N), overflow (V), and zero (Z) bits specifically. For example, 
the JMPC (jump if carry) instruction will jump to the specified address if the carry 
bit in the status register is a “1”. The JMPNC (jump if not carry) instruction will 
only jump if the carry bit in the status register is a “0”. This same pattern 
continues for each of the status bits.

Example: `JMP M[Ri, 0x0];`

This instruction will jump unconditionally to the address located in R2.

Example: `JZ M[Ri, 0x0];`

This instruction will jump to the address located in R1 if the zero bit is currently a "1".

##### -Labels

Labels allow jumping to different sections of code much easier. To define a label, just
write the label variable name on the destination line of code making sure to precede the 
instruction. The label identifier should be immediately followed by a colon.

Jumping to a label is just as easy. Just make the operand of any jump instruction the name
of the label, preceded by the '@' symbol.

Example:

```
LabelName: 	DEC R1;
			JNZ @LabelName;
```

#### -Emulated Instructions

These instructions are not actually additional instructions that the CPU knows about, but
they may make the assembly code easier to write and more understandable.

> NOP, INC, DEC, SHLA, CLR

NOP (no operation): `NOP;` --> `ADDC R0, 0x0;`

INC (increment): `INC Ri;` --> `ADDC Ri, 0x1;`

DEC (decrement): `DEC Ri;` --> `SUBC Ri, 0x1;`

SHLA (shift left arithmetic): `SHLA Ri;` --> `ADD Ri, Ri;`

CLR (clear): `CLR Ri;` --> `SUB Ri, Ri;`

#### -Skip

Skip is a special assembler command that is placed within the code block. This effectively
skips initializing the given number of addresses in memory.

Example: `.skip 0x10` 

This will skip 16 addresses in the assembled file, then continue writing the program
proceeding the skipped addresses. All skipped addresses are not-initialized to any value.

#### -Example Program

This small example program takes two values from memory (that are pre-initialized in the constants section)
and multiplies them together. It then stores the result back into memory.

```
.directives
	operand1 	0x100;
	operand2 	0x101;
	result		0x102;
.enddirectives

.constants
	0x100 0xA;
	0x101 0x5;
.endconstants

.code
	Start: 	LD R1, M[R0, $operand1];
			LD R2, M[R0, $operand2];
			CLR R3;
			ADDC R1, 0x0;
			JZ @Done;
			ADDC R2, 0x0;
			JZ @Done;
	Mult:	ADD R3, R1;
			DEC R2;
			JNZ @Mult;
	Done:	ST M[R0, $result], R3;
.endcode
```