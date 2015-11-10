import re

import Common

REGISTER_WIDTH = 12

class Instruction:

	Line = ""
	Mnemonic = ""
	MachineCode = ""

	JumpCode = None
	Offset = None
	OpCode = None
	Operand1 = None
	Operand2 = None

	SkipNumber = 0x0

	InsertAddress = -1
	InsertValue = 0x0

	Split = []

	RegisterMap = { "R0" : 0x0,
					"R1" : 0x1,
					"R2" : 0x2,
					"R3" : 0x3,
					"R4" : 0x4,
					"R5" : 0x5,
					"R6" : 0x6,
					"R7" : 0x7 }

	# This encodes the instruction mnemonic to the opcode
	InstructionList = {	"LD" 	: 0x0, 
						"ST" 	: 0x1,
						"CPY" 	: 0x2,
						"SWAP"	: 0x3,
						"JU"	: 0x4,
						"JZ"	: 0x4,
						"JNZ"	: 0x4,
						"JC"	: 0x4,
						"JNC"	: 0x4,
						"JV"	: 0x4,
						"JNV"	: 0x4,
						"JN"	: 0x4,
						"JNN"	: 0x4,
						"ADD"	: 0x5,
						"SUB"	: 0x6,
						"ADDC"	: 0x7,
						"SUBC"	: 0x8,
						"NOT"	: 0x9,
						"AND"	: 0xA,
						"OR"	: 0xB,
						"SHRA"	: 0xC,
						"ROTR"	: 0xD,
						"ADDV"	: 0xE,
						"NOP" 	: 0xF,
						"INC"	: 0xF,
						"DEC"	: 0xF,
						"SHLA"	: 0xF,
						"CLR"	: 0xF,
						".SKIP"	: 0xF,
						".INSERT" : 0xF }

	# This list encodes the jump instructions to the special CNVZ field in the IW
	JumpList = { 	"JU"	: 0x0,
					"JC"	: 0x8,
					"JN"	: 0x4,
					"JV"	: 0x2,
					"JZ"	: 0x1,
					"JNC"	: 0x7,
					"JNN"	: 0xB,
					"JNV"	: 0xD,
					"JNZ"	: 0xE }

	def __init__(self, line):
		self.Line = line
		self.GetOpCode()
		self.Decode()
		self.Assemble()

	def __str__(self):
		string = "%s (%s): %s" % (self.Mnemonic, str(self.OpCode), str(self.Operand1))
		if self.Operand2 != None:
			string += " %s" % str(self.Operand2)
		if self.Offset != None:
			string += " +%s" % str(self.Offset)
		string += " = %s" % self.MachineCode
		return string

	def __repr__(self):
		return str(self)

	def Assemble(self):
		machineCode = ""

		if self.SkipNumber:
			self.MachineCode = self.SkipNumber
			return
		if self.InsertAddress >= 0:
			return
		if self.OpCode == None or self.Operand1 == None:
			Common.Error(self.Line, "Invalid OpCode / Operand 1")
		else:
			machineCode += Common.NumToBinaryString(self.OpCode, 4) # OpCode
			machineCode += Common.NumToBinaryString(self.Operand1, 3) # Ri

		if self.Operand2 != None:
			machineCode += Common.NumToBinaryString(self.Operand2, 3) # Rj
		elif self.JumpCode != None:
			machineCode += Common.NumToBinaryString(self.JumpCode, 4)
		elif self.Mnemonic == "NOT":
			machineCode += "000" # Not only has one operand
		else:
			Common.Error(self.Line, "Missing jump code or second operand")

		offsetLen = REGISTER_WIDTH - len(machineCode)
		if self.Offset != None:
			machineCode += Common.NumToBinaryString(self.Offset, offsetLen)
		else:
			machineCode += Common.NumToBinaryString(0, offsetLen)

		if len(machineCode) != REGISTER_WIDTH:
			Common.Error(self.Line, "HUSTON?!?")

		self.MachineCode = machineCode

	def Decode(self):
		self.Split = [piece for piece in re.split(" |,|\t", self.Line.String) if piece != '']
		if self.OpCode >= 0x0 and self.OpCode <= 0x1:
			self.DecodeDataTransfer()
		elif self.OpCode == 0x4:
			self.DecodeJump()
		elif (self.OpCode >= 0x5 and self.OpCode <= 0xE) or (self.OpCode == 0x2 or self.OpCode == 0x3): # CPY and SWP act the same as manipulation
			self.DecodeManipulation()
		else:
			self.DecodeEmulated()

	def DecodeDataTransfer(self):
		if len(self.Split) != 3 and len(self.Split) != 4:
				Common.Error(self.Line, "Unknown operands")
		elif self.Mnemonic == "LD":
			self.Operand2 = self.GetFirstRegister(self.Split[1])
			if len(self.Split) == 4:
				self.Operand1, self.Offset = self.GetOperandWithOffset(self.Split[2],self.Split[3])
			elif len(self.Split) == 3:
				self.Operand1, self.Offset = self.GetOperandWithOffset(self.Split[2])
		elif self.Mnemonic == "ST":
			if len(self.Split) == 4:
				self.Operand1, self.Offset = self.GetOperandWithOffset(self.Split[1],self.Split[2])
				self.Operand2 = self.GetFirstRegister(self.Split[3])
			elif len(self.Split) == 3:
				self.Operand1, self.Offset = self.GetOperandWithOffset(self.Split[1])
				self.Operand2 = self.GetFirstRegister(self.Split[2])
		else:
			Common.Error(self.Line, "Error in DecodeDataTransfer")

	def DecodeEmulated(self):
		if self.Mnemonic == "NOP":
			if len(self.Split) != 1:
				Common.Error(self.Line, "Wrong number of operands")
			self.OpCode = self.InstructionList["ADDC"]
			self.Operand1 = 0x0
			self.Operand2 = 0x0
		elif self.Mnemonic == "INC":
			if len(self.Split) != 2:
				Common.Error(self.Line, "Wrong number of operands")
			self.OpCode = self.InstructionList["ADDC"]
			self.Operand1 = self.GetFirstRegister(self.Split[1])
			self.Operand2 = 0x1
		elif self.Mnemonic == "DEC":
			if len(self.Split) != 2:
				Common.Error(self.Line, "Wrong number of operands")
			self.OpCode = self.InstructionList["SUBC"]
			self.Operand1 = self.GetFirstRegister(self.Split[1])
			self.Operand2 = 0x1
		elif self.Mnemonic == "SHLA":
			if len(self.Split) != 2:
				Common.Error(self.Line, "Wrong number of operands")
			self.OpCode = self.InstructionList["ADD"]
			self.Operand1 = self.GetFirstRegister(self.Split[1])
			self.Operand2 = self.GetFirstRegister(self.Split[1])
		elif self.Mnemonic == "CLR":
			if len(self.Split) != 2:
				Common.Error(self.Line, "Wrong number of operands")
			self.OpCode = self.InstructionList["SUB"]
			self.Operand1 = self.GetFirstRegister(self.Split[1])
			self.Operand2 = self.GetFirstRegister(self.Split[1])
		elif self.Mnemonic == ".SKIP":
			if len(self.Split) != 2:
				Common.Error(self.Line, "Wrong number of operands")
			self.SkipNumber = self.GetHexOperand(self.Split[1])
		elif self.Mnemonic == ".INSERT":
			if len(self.Split) != 3:
				Common.Error(self.Line, "Wrong number of operands")
			self.InsertAddress = self.GetHexOperand(self.Split[1])
			self.InsertValue = self.GetHexOperand(self.Split[2])
		else:
			Common.Error(self.Line, "Error in DecodeEmulated")

	def DecodeJump(self):
		if self.Mnemonic not in self.JumpList:
			Common.Error(self.line, "Unknown jump mnemonic")
		
		self.JumpCode = self.JumpList[self.Mnemonic]
		if len(self.Split) == 3:	# If we are provided an offset		
			self.Operand1, self.Offset = self.GetOperandWithOffset(self.Split[1],self.Split[2])
		elif len(self.Split) == 2: # If we are not provided an offset
			self.Operand1, self.Offset = self.GetOperandWithOffset(self.Split[1])
		else:
			Common.Error(self.Line, "Unknown operands")

	def DecodeManipulation(self):
		if self.Mnemonic == "ADD" or self.Mnemonic == "SUB" or self.Mnemonic == "AND" or self.Mnemonic == "OR" or self.Mnemonic == "CPY" or self.Mnemonic == "SWAP" or self.Mnemonic == "ADDV":
			if len(self.Split) != 3:
				Common.Error(self.Line, "Unknown operands")
			else:
				self.Operand1 = self.GetFirstRegister(self.Split[1])
				self.Operand2 = self.GetSecondRegister(self.Split[2])

		elif self.Mnemonic == "ADDC" or self.Mnemonic == "SUBC" or self.Mnemonic == "SHRA" or self.Mnemonic == "ROTR":
			if len(self.Split) != 3:
				Common.Error(self.Line, "Unknown operands")
			else:
				self.Operand1 = self.GetFirstRegister(self.Split[1])
				self.Operand2 = self.GetHexOperand(self.Split[2])

		elif self.Mnemonic == "NOT":
			if len(self.Split) != 2:
				Common.Error(self.Line, "Unknown operands")
			else:
				self.Operand1 = self.GetFirstRegister(self.Split[1])

		else:
			Common.Error(self.Line, "This should be impossible to get to")

	def GetOpCode(self):
		self.Mnemonic = self.Line.String.split()[0].upper()
		if self.Mnemonic not in self.InstructionList.keys():
			Common.Error(self.Line, "Unknown instruction: %s" % self.Mnemonic)
		else:
			self.OpCode = self.InstructionList[self.Mnemonic]

	def GetOperandWithOffset(self, operand, offset = "0x0"):
		operand = operand.replace("M[",'').replace(']','').replace(',','')
		operand = self.GetFirstRegister(operand)

		offset = offset.replace(']','').replace(',','')
		offset = self.GetHexOperand(offset)

		return operand, offset

	def GetFirstRegister(self, operand):
		if ',' in operand:
			operand = operand.replace(',','') # Removes the comma from the instruction if there is one
		return self.GetSecondRegister(operand)

	def GetHexOperand(self, operand):
		if not operand.startswith("0x"):
			Common.Error(self.Line, "Operand must be hex: %s" % operand)
		val = 0
		try:
			val = int(operand, 16)
		except ValueError:
			Common.Error(self.Line, "Operand must be hex: %s" % operand)		
		return val

	def GetSecondRegister(self, operand):
		if operand not in self.RegisterMap.keys():
				Common.Error(self.Line, "Unknown register: %s" % operand)
		else:
			return self.RegisterMap[operand]
