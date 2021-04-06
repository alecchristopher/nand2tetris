import os

class Parser(object):
	''' Class methods taken from Chapter 7 in book'''
	### FROM BOOK 
	def __init__(self, stream):
		'''Opens the input file/stream and gets ready to parse it.'''
		self.file = open(stream, 'r')
		self.current_command = None
		self.next_command = self.file.readline().strip().split()
		while(len(self.next_command) == 0 or self.next_command[0] == '//'):
			self.next_command = self.file.readline().strip().split()
		self.typeMap = {
			'add': 'C_ARITHMETIC',
			'sub': 'C_ARITHMETIC',
			'neg': 'C_ARITHMETIC',
			'eq': 'C_ARITHMETIC',
			'gt': 'C_ARITHMETIC',
			'lt': 'C_ARITHMETIC',
			'and': 'C_ARITHMETIC',
			'or': 'C_ARITHMETIC',
			'not': 'C_ARITHMETIC',
			'push': 'C_PUSH',
			'pop': 'C_POP',
			'label': 'C_LABEL',
			'goto': 'C_GOTO',
			'if-goto': 'C_IF',
			'function': 'C_FUNCTION',
			'return': 'C_RETURN',
			'call': 'C_CALL'
		}

	@property
	def hasMoreCommands(self):
		'''Are there more commands in the input?'''
		if(self.next_command == "EOF"):
			return False
		else:
			return True

	def advance(self):
		''' Reads the next command from the input and makes it
		the current command. Should be called only if
		hasMoreCommands() is true. Initially there is no
		current command.'''
		self.current_command = self.next_command
		self.next_command = self.file.readline().strip().split()
		endOfFileCount = 0
		while(len(self.next_command) == 0 or self.next_command[0] == '//'):
			self.next_command = self.file.readline().strip().split()
			if(endOfFileCount >= 20):
				self.next_command = "EOF"
				return
			endOfFileCount += 1

	@property
	def commandType(self):
		'''
		Returns the type of the current VM command.
		C_ARITHMETIC is returned for all the arithmetic commands.
		'''
		return self.typeMap.get(self.current_command[0].lower())

	@property
	def arg1(self):
		'''Returns the first argument of the current command. In
		the case of C_ARITHMETIC, the command itself (add,
		sub, etc.) is returned. Should not be called if the
		current command is C_RETURN.'''
		if(self.commandType == 'C_RETURN'):
			return
		elif(self.commandType == 'C_ARITHMETIC'):
			return self.current_command[0].strip()
		else:
			return self.current_command[1]

	@property
	def arg2(self):
		'''Returns the second argument of the current
		command. Should be called only if the current
		command is C_PUSH, C_POP, C_FUNCTION, or C_CALL.'''
		if(self.commandType in ['C_PUSH', 'C_POP', 'C_FUNCTION', 'C_CALL']):
			return self.current_command[2]

	####END BOOK

class CodeWriter(object):
	def __init__(self, stream):
		'''Opens the output file/ stream and gets ready to
		write into it.'''
		self.file = open(stream + '.asm', 'w')
		self.filename = stream
		self.bool_count = 0

	def setFileName(self, fileName):
		'''Informs the code writer that the translation of a
		new VM file is started.'''
		self.file.close()
		os.rename(self.filename + '.asm', fileName + '.asm')
		self.filename = fileName
		self.file = open(self.filename + '.asm', 'w')

	def writeComment(self, command):
		for text in command:
			self.file.write(text)
		self.file.write("\n")

	def writeArithmetic(self, command):
		'''Writes the assembly code that is the translation 
		of the given arithmetic command.'''
		if command not in ['neg', 'not']: # neg and not only need to pop stack once
			# pop the stack and set value to D
			# equivalent : y = stack.pop()
			self.file.write('@SP'+ '\n')
			self.file.write('M=M-1'+ '\n') # decrement sp
			self.file.write('A=M'+ '\n')   # set address to current stack pointer
			self.file.write('D=M'+ '\n')   # get data from top of stack

		# decrement sp and set A to top of stack
		# equivalent: set x = top of stack
		self.file.write('@SP'+ '\n')
		self.file.write('M=M-1'+ '\n') # decrement sp
		self.file.write('@SP'+ '\n')
		self.file.write('A=M'+ '\n')   # set address to current stack pointer

		# at this state D has the arg2 and A/M has arg 1
		if command == "add":
			self.file.write('M=M+D' + '\n')
		elif command == "sub":
			self.file.write('M=M-D' + '\n')
		elif command == 'and':
			self.file.write('M=M&D'+ '\n')
		elif command == 'or':
			self.file.write('M=M|D'+ '\n')
		elif command == 'neg':
			self.file.write('M=-M'+ '\n')
		elif command == 'not':
			self.file.write('M=!M'+ '\n')
		elif command in ['eq', 'gt', 'lt']:
			'''The VM represents true and false as -1 (minus one, 0xFFFF ) 
			and 0 (zero, 0x0000), respectively.'''
			'''
			I had a very hard time writing this hack translation. This code was 
			adapted from "https://github.com/kronosapiens/nand2tetris/blob/master/projects/07/VMtranslator.py"
			this solution seemed the most optomized.
			'''
			self.file.write('D=M-D'+ '\n')
			self.file.write('@BOOL{}'.format(self.bool_count)+ '\n')

			if command == 'eq':
				self.file.write('D;JEQ'+ '\n') # if x == y, x - y == 0
			elif command == 'gt':
				self.file.write('D;JGT'+ '\n') # if x > y, x - y > 0
			elif command == 'lt':
				self.file.write('D;JLT'+ '\n') # if x < y, x - y < 0

			self.file.write('@SP'+ '\n')
			self.file.write('A=M'+ '\n')   # set address to current stack pointer
			self.file.write('M=0'+ '\n') # False
			self.file.write('@ENDBOOL{}'.format(self.bool_count)+ '\n')
			self.file.write('0;JMP'+ '\n')

			self.file.write('(BOOL{})'.format(self.bool_count)+ '\n')
			self.file.write('@SP'+ '\n')
			self.file.write('A=M'+ '\n')   # set address to current stack pointer
			self.file.write('M=-1'+ '\n') # True

			self.file.write('(ENDBOOL{})'.format(self.bool_count)+ '\n')
			self.bool_count += 1

		# increment sp
		self.file.write('@SP'+ '\n')
		self.file.write('M=M+1'+ '\n') 

	def writePushPop(self, command, segment, index):
		'''Writes the assembly code that is the translation of
		the given command, where command is either C_PUSH or C_POP.'''
		self.resolve_address(segment, index)
		if command == 'C_PUSH': # load M[address] to D
			if segment == 'constant':
				self.file.write('D=A'+ '\n')
			else:
				self.file.write('D=M'+ '\n')

			self.file.write('@SP'+ '\n') # Get current stack pointer
			self.file.write('A=M'+ '\n') # Set address to current stack pointer
			self.file.write('M=D'+ '\n') # Write data to top of stack
			self.file.write('@SP'+ '\n') # Increment SP
			self.file.write('M=M+1'+ '\n')

		elif command == 'C_POP': # load D to M[address]
			self.file.write('D=A'+ '\n')
			self.file.write('@R13'+ '\n') # Store resolved address in R13
			self.file.write('M=D'+ '\n')
			self.file.write('@SP'+ '\n')
			self.file.write('M=M-1'+ '\n') # decrement sp
			self.file.write('A=M'+ '\n')   # set address to current stack pointer
			self.file.write('D=M'+ '\n')   # get data from top of stack
			self.file.write('@R13'+ '\n')
			self.file.write('A=M'+ '\n')
			self.file.write('M=D'+ '\n')

	def resolve_address(self, segment, index):
		'''Resolve address to A register'''
		addrs = {
            'local': 'LCL', # Base R1
            'argument': 'ARG', # Base R2
            'this': 'THIS', # Base R3
            'that': 'THAT', # Base R4
            'pointer': 3, # Edit R3, R4
            'temp': 5, # Edit R5-12
            # R13-15 are free
            'static': 16, # Edit R16-255
        }
		address = addrs.get(segment)
		
		if segment == 'constant':
			self.file.write('@' + str(index)+ '\n')
		elif segment == 'static':
			self.file.write('@' + os.path.basename(file_path).rsplit('.', 1)[0] + '.' + str(index)+ '\n')
		elif segment in ['pointer', 'temp']:
			self.file.write('@R' + str(address + int(index))+ '\n') # Address is an int
		elif segment in ['local', 'argument', 'this', 'that']:
			self.file.write('@' + address+ '\n') # Address is a string
			self.file.write('D=M'+ '\n')
			self.file.write('@' + str(index)+ '\n')
			self.file.write('A=D+A'+ '\n') # D is segment base

	def close(self):
		self.file.close()


if __name__ == '__main__':
	import sys

	file_path = sys.argv[1]
	basename = os.path.basename(file_path).rsplit('.', 1)[0]

	parser = Parser(file_path)
	writer = CodeWriter(basename)

	while(parser.hasMoreCommands):
		parser.advance()
		writer.writeComment(["//"] + parser.current_command)
		if(parser.commandType == 'C_ARITHMETIC'):
			writer.writeArithmetic(parser.arg1)
		else:
			writer.writePushPop(parser.commandType, parser.arg1, parser.arg2)

	writer.close()
		
# Sample Execution

# $ python VMTranslator.py <Path>/File.vm
