import Common

class Mif():
	OutputFile = ""
	Headers = []

	Width = 0
	Depth = 0
	DataRadix = ""

	Data = []

	def __init__(self, output, width, depth, headers = []):
		self.OutputFile = output
		self.Width = width
		self.Depth = depth
		#self.DataRadix = dataRadix
		self.DataRadix = "HEX"
		self.Headers = headers

	def AddData(self, dataList):
		self.Data += dataList
		return self

	def Write(self):
		with open(self.OutputFile, "w+") as _file:
			_file.seek(0)
			_file.truncate() # Clears out the file if it exists
			_file.write("-- Assembled for RISC521 by Connor Goldberg\n")

			for line in self.Headers:
				_file.write("-- %s\n" % line)

			_file.write("\nWIDTH = %s;\n" % str(self.Width))
			_file.write("DEPTH = %s;\n" % str(self.Depth)) #TODO: Check to see if number of instts is less than depth
			_file.write("ADDRESS_RADIX = HEX;\n")
			_file.write("DATA_RADIX = %s;\n" % str(self.DataRadix))
			_file.write("\nCONTENT BEGIN\n")
			_file.write("\n")

			counter = 0
			for data,comment in self.Data:
				if comment.upper().startswith(".SKIP"):
					counter += data
					_file.write("-- Skipping 0x%s addresses\n" % Common.NumToHexString(data))
					continue
				elif comment.upper().startswith(".INSERT"):
					_file.write("%s : %s; %% %s %%\n" % (data[0], data[1], comment))
					continue
				elif comment.upper().startswith(".CONSTANT"):
					_file.write("%s : %s;\n" % (data[0], data[1]))
					continue
				line = Common.NumToHexString(counter, 2)
				line += " : %s;" % data

				if comment:
					line += " %% %s %%\n" % comment
				else:
					line += "\n"

				_file.write(line)

				counter+=1

			_file.write("\nEND;\n")

		return self