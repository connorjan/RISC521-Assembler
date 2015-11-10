#!/usr/bin/env python
import argparse
import atexit
import os
from time import clock

import Common
import Mif
import Parser

"""
Title: Assembler for RISC521
Author: Connor Goldberg
"""

def main(args):
	start = clock()

	assemblyFile = args["assembly-file"]
	output = args["output"]
	if output == None:
		output = os.path.join(os.path.split(os.path.abspath(assemblyFile))[0],os.path.splitext(os.path.basename(assemblyFile))[0]+".mif")
	elif not output.endswith(".mif"):
		output += ".mif"

	myParser = Parser.Parser(assemblyFile)	
	programMif = Mif.Mif(output, args["width"], args["depth"], ["Program memory for: %s" % assemblyFile])
	myParser.Parse()
	programMif.AddData(myParser.GetAssemblyData()).AddData(myParser.GetConstantsData()).Write()

	end = clock()

	print "Successfully assembled %s into %s" % (assemblyFile, output)
	print "Time elapsed: %s ms" % str(round(float(end-start)*1000,3))

if __name__ == "__main__":
	

	parser = argparse.ArgumentParser(description="Assembler for RISC521 by Connor Goldberg")
	parser.add_argument("assembly-file", help="File to be assembled")
	parser.add_argument("-o", "--output", metavar="out-file", type=str, help="The path of the MIF file")
	parser.add_argument("-d", "--depth", metavar="depth", type=int, help="The depth of the output file", default=1024)
	parser.add_argument("-w", "--width", metavar="width", type=int, help="The width of instruction words", default=12)
	args = vars(parser.parse_args())
	main(args)