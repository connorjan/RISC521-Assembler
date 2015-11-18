import os
from collections import OrderedDict

import Common
import Instruction

class Line:
	Number = -1
	String = ""

	def __init__(self, number, string):
		self.Number = number
		self.String = string

	def __str__(self):
		return "%s : %s" % (str(self.Number),self.String)

	def __repr__(self):
		return str(self)

class Assembly:

	Original = []
	WithoutComments = []

	Code = []
	ConstantsLines = []
	DirectivesLines = []

	Constants = []
	Directives = {}
	Labels = {}

	Instructions = []

	def __init__(self):
		pass

	def __str__(self):
		string = ""

		if self.ConstantsLines:
			string += "Constants:"
			for line in self.ConstantsLines:
				string += "\n\t%s" % line
			string += "\n"
		if self.DirectivesLines:
			string += "Directives:"
			for line in self.DirectivesLines:
				string += "\n\t%s" % line
			string += "\n"
		if self.Code:
			string += "Code:"
			for line in self.Code:
				string += "\n\t%s" % line

		return string

	def __repr__(self):
		return str(self)

	def Decode(self):
		self.DecodeConstants()
		self.DecodeDirectives()
		self.DecodeCode()

	def DecodeConstants(self):
		for constant in self.ConstantsLines:
			split = constant.String.split()
			if len(split) != 2:
				Common.Error(constant, "Wrong syntax for constant")
			elif not split[0].startswith("0x") or not split[1].startswith("0x"):
				Common.Error(constant, "Constants must be hex")
			else:
				self.Constants.append((split[0],split[1]))

	def DecodeDirectives(self):
		for directive in self.DirectivesLines:
			split = directive.String.split()
			if len(split) != 2:
				Common.Error(directive, "Wrong syntax for directive")
			else:
				self.Directives[split[0]] = split[1]

	def DecodeCode(self):
		newCode = []
		for line in self.Code:
			for directive, value in self.Directives.iteritems():
				toBeReplaced = "$" + directive
				if toBeReplaced in line.String:
					line.String = line.String.replace(toBeReplaced, self.Directives[directive])
				if line.String.endswith(':'):
					Common.Error(line, "Label must be on the same line as an instruction")
			self.Instructions.append(Instruction.Instruction(line))
			newCode.append(line)
		self.Code = newCode

	def ResolveLabels(self):
		addressCounter = 0
		# Pass 1, get the address associated with each label
		for instruction in self.Instructions:
			if instruction.LabelWord:
				instruction.LabelAddress = addressCounter
				self.Labels[instruction.LabelWord] = instruction.LabelAddress
			addressCounter += instruction.InstructionList[instruction.Mnemonic][1]
		# Pass 2, resolve the label
		for instruction in self.Instructions:
			if instruction.NeedsLabelLookup:
				if instruction.LabelOffset[1:] in self.Labels.keys():
					instruction.Offset = self.Labels[instruction.LabelOffset[1:]]
				else:
					Common.Error(instruction.Line, "Could not find matching label for: %s" % instruction.LabelOffset)

class Parser:

	AssemblyFilePath = ""
	MyAssembly = Assembly()

	def __init__(self, assemblyFilePath):
		self.AssemblyFilePath = assemblyFilePath

	def FileToLines(self, assemblyFilePath):
		if os.path.isfile(assemblyFilePath):
			with open(assemblyFilePath) as _file:
				lineCount = 1
				for line in _file:
					self.MyAssembly.Original.append(Line(lineCount, line.strip()))
					lineCount+=1
		else: 
			return []

	def GetAssemblyData(self):
		lines = []

		for instruction in self.MyAssembly.Instructions:
			if instruction.SkipNumber:
				data = instruction.SkipNumber
			elif instruction.InsertAddress >= 0:
				data = (Common.NumToHexString(instruction.InsertAddress), Common.NumToHexString(instruction.InsertValue),4)
			else:
				data = Common.NumToHexString(int(instruction.MachineCode, 2), 4)	
			comment = instruction.Line.String
			lines.append((data,comment))

			if instruction.Offset != None:
				data = Common.NumToHexString(instruction.Offset, 4);
				comment = ""
				lines.append((data,comment))

		return lines

	def GetConstantsData(self):
		lines = []

		for constant in self.MyAssembly.Constants:
			lines.append(((constant[0][2:], constant[1][2:]), ".CONSTANT %s %s" % (constant[0], constant[1])))
		return lines

	def RemoveComments(self):
		pass1 =  [line for line in self.MyAssembly.Original if not line.String.startswith(";") and not line.String.startswith("//")] # Removes all lines starting with semicolons
		pass2 = []
		for line in pass1:
			if ';' in line.String:
				line.String = line.String[:line.String.index(';')] # Removes semicolon comments
			if "//" in line.String:
				line.String = line.String[:line.String.index("//")] # Removes // comments
			pass2.append(line)

		return [line for line in pass2 if line.String != ""] # Remove empty lines

	def Separate(self):
		category = Common.Enum("Directives", "Constants", "Code")
		myCategory = None

		for line in self.MyAssembly.WithoutComments:
			if line.String.startswith('.directives'):
				myCategory = category.Directives
			elif line.String.startswith('.constants'):
				myCategory = category.Constants
			elif line.String.startswith('.code'):
				myCategory = category.Code
			elif line.String.startswith('.enddirectives') or line.String.startswith('.endconstants') or line.String.startswith('.endcode'):
				myCategory = None
			else:
				if myCategory == category.Directives:
					self.MyAssembly.DirectivesLines.append(line)
				elif myCategory == category.Constants:
					self.MyAssembly.ConstantsLines.append(line)
				elif myCategory == category.Code:
					self.MyAssembly.Code.append(line)
				else:
					Common.Error(line, "Line \"%s\" belongs to unknown section" % line.String)

	def Parse(self):

		self.FileToLines(self.AssemblyFilePath)
		self.MyAssembly.WithoutComments = self.RemoveComments()
		self.Separate()
		self.MyAssembly.Decode()
		self.MyAssembly.ResolveLabels()