import re

class Lexer:
    def  __init__(self, filename):
        self.filename = filename
        self.commands = []

    def process(self):
        with open(self.filename, "r") as file:
            for raw in file:
                if(len(raw) == 1):
                    continue
                line = re.sub(r"[\n\t\s]+", " ", raw)
                line = re.sub(r"//.*", "", line)
                if len(line) > 0:
                    command = line.strip().split()
                    self.commands.append(command)
        print(self.commands)
        return self.commands

class Parser:

    def __init__(self, listOfCommands):
        self.list_len = len(listOfCommands)
        self.commands = listOfCommands
        self.curr_index = 0
        self.current_command = ""
        self.type_map = self.type_map()

    def hasMoreCommands(self):
        if self.curr_index < self.list_len:
            return True
        return False

    def advance(self):
        if(self.curr_index < self.list_len):
            self.current_command = self.commands[self.curr_index]
            self.curr_index += 1

    def command_type(self):
        return self.type_map.get(self.current_command[0])

    def arg1(self):
        return self.current_command[1]

    def arg2(self):
        return self.current_command[2]

    def type_map(self):
        return {
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

class CodeWriter:
    def __init__(self):
        self.code_string = ""
        self.filename = ""
        self.counter = 0
        self.seg_map = {
            'local' : 'LCL',
            'argument' : 'ARG',
            'this' : 'THIS',
            'that' : 'THAT'
            }
        #self.write__init()

    def write_init(self):
        self.code_string += "SP=256 \n"
        # TODO
        pass

    def set_filename(self, name):
        self.filename = name

    def write_arithmetic(self, command):
        if( command== "add" ):
            self.code_string += self.write_add()
        elif ( command== "sub"):
            self.code_string += self.write_sub()
        elif ( command== "neg"):
            self.code_string += self.write_neg()
        elif ( command== "and"):
            self.code_string += self.write_and()
        elif ( command== "or"):
            self.code_string += self.write_or()
        elif ( command== "not"):
            self.code_string += self.write_not()
        elif ( command== "gt"):
            self.code_string += self.write_gt()
        elif ( command== "lt"):
            self.code_string += self.write_lt()
        elif ( command== "eq"):
            self.code_string += self.write_eq()

    def write_push_pop(self, command, segment, index):
        if(command == "push"):
            self.code_string += self.write_push(segment, index)
        elif(command == "pop"):
            self.code_string += self.write_pop(segment, index)

    def write_label(self, label):
        str = ""
        str += "({}) \n".format(label)
        self.code_string += str

    def write_goto(self, label):
        str = ""
        str += "@{} \n".format(label)
        str += "0;JMP \n"
        self.code_string += str
    
    def write_if(self, label):
        str = ""
        # Pop Into D
        str += ("@SP \n")
        str += ("M=M-1 \n")
        str += ("A=M \n")
        str += ("D=M \n")
        # Declare jump to Label
        str += ("@{} \n".format(label))
        # Compare With 0
        str +=  ("D;JNE \n")
        self.code_string += str

    def write_call(self, functionName, numArgs):
       str = ""
       # push return-address -------------------
       str += "@{}.{} \n".format(functionName,self.counter)
       str += "D=A \n"
       # push D to stack
       str += "@SP \n"
       str += "A=M \n"
       str += "M=D \n"
       # Inc. SP
       str += "@SP \n"
       str += "M=M+1 \n"

       # push LCL -------------------
       str += "@LCL \n"
       str += "D=M \n"
       # push D to stack
       str += "@SP \n"
       str += "A=M \n"
       str += "M=D \n"
       # Inc. SP
       str += "@SP \n"
       str += "M=M+1 \n"


       # push ARG -------------------
       str += "@ARG \n"
       str += "D=M \n"
       # push D to stack
       str += "@SP \n"
       str += "A=M \n"
       str += "M=D \n"
       # Inc. SP
       str += "@SP \n"
       str += "M=M+1 \n"

       # push THIS -------------------
       str += "@THIS \n"
       str += "D=M \n"
       # push D to stack
       str += "@SP \n"
       str += "A=M \n"
       str += "M=D \n"
       # Inc. SP
       str += "@SP \n"
       str += "M=M+1 \n"

       # push THAT -------------------
       str += "@THAT \n"
       str += "D=M \n"
       # push D to stack
       str += "@SP \n"
       str += "A=M \n"
       str += "M=D \n"
       # Inc. SP
       str += "@SP \n"
       str += "M=M+1 \n"


       # ARG = SP-n-5
       str += "@{} \n".format(int(numArgs) + 5)
       str += "D=A \n"
       str += "@SP \n"
       str += "D=M-D \n"
       str += "@ARG \n"
       str += "M=D \n"

       # LCL = SP
       str += "@SP \n"
       str += "D=M \n"
       str += "@LCL \n"
       str += "M=D \n"

       self.code_string += str

       # goto f
       self.write_goto(functionName)

       # Retrun Label
       self.code_string += "({}.{}) \n".format(functionName,self.counter)

    def write_function(self, functionName, numVars):
        str = ""
        # Declare Label For Function
        str += "({}) \n".format(functionName)
        # initilize k variables to 0 on the stack
        str += "@SP \n"
        str += "A=M \n"
        for i in range(int(numVars)):
            str += "M=0 \n"
            str += "A=A+1 \n"
        # set SP to after k vars
        str += "D=A \n"
        str += "@SP \n"
        str += "M=D \n"
        self.code_string += str

    def write_return(self):
        str = ""
        # FRAME a.k.a R13 = LCL
        str += "@LCL \n"
        str += "D=M \n"
        str += "@R14 \n"
        str += "M=D \n"
        # RET = *(FRAME-5)
        str += "@R14 \n"
        str += "D=M \n"
        str += "@5 \n"
        str += "D=D-A \n"
        str += "@R15 \n"
        str += "M=D \n"
        # *ARG = pop()
        self.code_string += str
        self.write_pop("arguement", 0)
        str = ""
        # SP = ARG+1
        str += "@ARG \n"
        str += "D=M+1 \n"
        str += "@SP \n"
        str += "M=D  \n"
        # THAT = *(FRAME-1), THIS = *(FRAME - 2), etc..
        map = ['', 'THAT', 'THIS', 'ARG', 'LCL']
        for i in (1, 2, 3, 4):
            str += "@R14 \n"
            str += "D=M \n"
            str += "@{} \n".format(map[i])
            str += "M=D \n"
            str += "@{} \n".format(i)
            str += "D=A \n"
            str += "@{} \n".format(map[i])
            str += "M=M-D \n"
        # goto RET
            str += "@R15 \n"
            str += "A=M \n"
            str += "0;JMP \n";

        self.code_string += str

    def write_init(self):
        str = ""
        str += "@256 \n"
        str += "D=A \n"
        str += "@SP \n"
        str += "M=D \n"
        self.code_string += str
        self.write_call("Sys.init", 0)

    def close(self):
        file = open(self.filename, 'w')
        file.write(self.code_string)
        file.close()

    def write_push(self, segment, index):
        str = ""
        if(segment == "constant"):
            str += ("// push constant {}\n".format(index))
            # Load immediate value into the D register
            str += "@{} \n".format(index)
            str += "D=A \n"
            # Set the Value of segment to D
            str += "@SP \n"
            str += "A=M \n"
            str += "M=D \n"
            # Inc. Stack
            str += ("@SP \n")
            str += ("M=M+1 \n")

        elif(segment in ["local", "argument", "this", "that"]):
            str += ("// push {} {}\n".format(segment, index))
            # Go to local[index]
            str += ("@{} \n".format(self.seg_map.get(segment)))
            str += ("D=M \n")
            str += "@{} \n".format(index)
            str += ("A=D+A \n")
            # Set Value of D to local[index]
            str += ("D=M \n")
            # Push D To top of Stack
            str += ("@SP \n")
            str += ("A=M \n")
            str += ("M=D \n")
            # Inc. Stack
            str += ("@SP \n")
            str += ("M=M+1 \n")

        elif(segment == "pointer"):
            str += ("// push {} {}\n".format(segment, index))
            # Go to local[index]
            str += ("@{} \n".format(index))
            str += ("D=A \n")
            str += "@3 \n"
            str += ("A=D+A \n")
            # Set Value of D to local[index]
            str += ("D=M \n")
            # Push D To top of Stack
            str += ("@SP \n")
            str += ("A=M \n")
            str += ("M=D \n")
            # Inc. Stack
            str += ("@SP \n")
            str += ("M=M+1 \n")

        elif(segment == "temp"):
            str += ("// push {} {}\n".format(segment, index))
            # Go to local[index]
            str += ("@{} \n".format(index))
            str += ("D=A \n")
            str += "@5 \n"
            str += ("A=D+A \n")
            # Set Value of D to local[index]
            str += ("D=M \n")
            # Push D To top of Stack
            str += ("@SP \n")
            str += ("A=M \n")
            str += ("M=D \n")
            # Inc. Stack
            str += ("@SP \n")
            str += ("M=M+1 \n")

        elif(segment == "static"):
            str += ("// push {} {}\n".format(segment, index))
            # Assign Symbol
            str += ("@{}.{} \n".format(self.filename, index))
            str += ("D=M \n")
            # Push D To top of Stack
            str += ("@SP \n")
            str += ("A=M \n")
            str += ("M=D \n")
            # Inc. Stack
            str += ("@SP \n")
            str += ("M=M+1 \n")

        return str

    def write_pop(self, segment, index):
        str = ""
        if(segment in ["local", "argument", "this", "that"]):
            str += "//pop {} {} \n".format(segment, index)
            # Decrement Stack
            str += "@SP \n"
            str += "M=M-1 \n"
            # Go to local[index]
            str += "@{} \n".format(self.seg_map.get(segment))
            str += "D=M \n"
            str += "@{} \n".format(index)
            str += "D=D+A \n"
            # Set value of r13 to local[index]*
            str += "@R13 \n"
            str += "M=D \n"
            str += "@SP \n"
            str += "A=M \n"
            # Set D to top of Stack
            str += "D=M \n"
            # Set local[index] = D
            str += "@R13 \n"
            str += "A=M \n"
            str += "M=D \n"

        elif(segment == "pointer"):
            str += "//pop {} {} \n".format(segment, index)
            # Decrement Stack
            str += "@SP \n"
            str += "M=M-1 \n"
            # Go to local[index]
            str += ("@{} \n".format(index))
            str += ("D=A \n")
            str += "@3 \n"
            str += ("D=D+A \n")
            # Set value of r13 to local[index]*
            str += "@R13 \n"
            str += "M=D \n"
            str += "@SP \n"
            str += "A=M \n"
            # Set D to top of Stack
            str += "D=M \n"
            # Set local[index] = D
            str += "@R13 \n"
            str += "A=M \n"
            str += "M=D \n"

        elif(segment == "temp"):
            str += "//pop {} {} \n".format(segment, index)
            # Decrement Stack
            str += "@SP \n"
            str += "M=M-1 \n"
            # Go to local[index]
            str += ("@{} \n".format(index))
            str += ("D=A \n")
            str += "@5 \n"
            str += ("D=D+A \n")
            # Set value of r13 to local[index]*
            str += "@R13 \n"
            str += "M=D \n"
            str += "@SP \n"
            str += "A=M \n"
            # Set D to top of Stack
            str += "D=M \n"
            # Set local[index] = D
            str += "@R13 \n"
            str += "A=M \n"
            str += "M=D \n"

        elif(segment == "static"):
            str += ("// pop {} {}\n".format(segment, index))
            # Pop Stack Onto D
            str += "@SP \n"
            str += "M=M-1 \n"
            str += "A=M \n"
            str += "D=M \n"
            # Load D into Symbol
            str += "@{}.{} \n".format(self.filename, index)
            str += "M=D \n"

        return str

    def write_add(self):
        str = ""
        str += ("// add \n")
        # Pop Into D
        str += ("@SP \n")
        str += ("M=M-1 \n")
        str += ("A=M \n")
        str += ("D=M \n")
        # Replace Top With Summation
        str += ("@SP \n")
        str += ("M=M-1 \n")
        str += ("A=M \n")
        str += ("M=D+M \n")
        # Inc. Stack
        str += ("@SP \n")
        str += ("M=M+1 \n")
        return str

    def write_sub(self):
        str = ""
        str += ("// sub \n")
        # Pop Into D
        str += ("@SP \n")
        str += ("M=M-1 \n")
        str += ("A=M \n")
        str += ("D=M \n")
        # Replace Top With Summation
        str += ("@SP \n")
        str += ("M=M-1 \n")
        str += ("A=M \n")
        str += ("M=M-D \n")
        # Inc. Stack
        str += ("@SP \n")
        str += ("M=M+1 \n")
        return str
        
    def write_neg(selg):
        str = ""
        str += ("// neg \n")
        # Replace Top With Negation
        str += ("@SP \n")
        str += ("M=M-1 \n")
        str += ("A=M \n")
        str += ("M=-M \n")
        # Inc. Stack
        str += ("@SP \n")
        str += ("M=M+1 \n")
        return str

    def write_and(self):
        str = ""
        str += ("// and \n")
        # Pop Into D
        str += ("@SP \n")
        str += ("M=M-1 \n")
        str += ("A=M \n")
        str += ("D=M \n")
        # Replace Top With Logical And
        str += ("@SP \n")
        str += ("M=M-1 \n")
        str += ("A=M \n")
        str += ("M=D&M \n")
        # Inc. Stack
        str += ("@SP \n")
        str += ("M=M+1 \n")
        return str

    def write_or(self):
        str = ""
        str += ("// or \n")
        # Pop Into D
        str += ("@SP \n")
        str += ("M=M-1 \n")
        str += ("A=M \n")
        str += ("D=M \n")
        # Replace Top With Logical Or
        str += ("@SP \n")
        str += ("M=M-1 \n")
        str += ("A=M \n")
        str += ("M=D|M \n")
        # Inc. Stack
        str += ("@SP \n")
        str += ("M=M+1 \n")
        return str

    def write_not(self):
        str = ""
        str += ("// not \n")
        # Replace Top With Logical Not
        str += ("@SP \n")
        str += ("M=M-1 \n")
        str += ("A=M \n")
        str += ("M=!M \n")
        # Inc. Stack
        str += ("@SP \n")
        str += ("M=M+1 \n")
        return str

    def write_gt(self):
        str = ""
        str += ("// gt \n")
        # Pop Into D
        str += ("@SP \n")
        str += ("M=M-1 \n")
        str += ("A=M \n")
        str += ("D=M \n")
        # Subtract x- y
        str += ("@SP \n")
        str += ("M=M-1 \n")
        str += ("A=M \n")
        str += ("D=M-D \n")
        # Compare
        str += ("@True_{} \n".format(self.counter))
        str += ("D;JGT \n")
        str += ("D=0 \n")
        str += ("@Then_{} \n".format(self.counter))
        str += ("0;JMP \n")
        str += ("(True_{}) \n".format(self.counter))
        str += ("D=-1 \n")
        str += ("(Then_{}) \n".format(self.counter))
        # Push D (result of comparison) onto stack
        str += ("@SP \n")
        str += ("A=M \n")
        str += ("M=D \n")
        # Inc. Stack
        str += ("@SP \n")
        str += ("M=M+1 \n")
        self.counter +=1
        return str

    def write_lt(self):
        str = ""
        str += ("// lt \n")
        # Pop Into D
        str += ("@SP \n")
        str += ("M=M-1 \n")
        str += ("A=M \n")
        str += ("D=M \n")
        # Subtract x- y
        str += ("@SP \n")
        str += ("M=M-1 \n")
        str += ("A=M \n")
        str += ("D=M-D \n")
        # Compare
        str += ("@True_{} \n".format(self.counter))
        str += ("D;JLT \n")
        str += ("D=0 \n")
        str += ("@Then_{} \n".format(self.counter))
        str += ("0;JMP \n")
        str += ("(True_{}) \n".format(self.counter))
        str += ("D=-1 \n")
        str += ("(Then_{}) \n".format(self.counter))
        # Push D (result of comparison) onto stack
        str += ("@SP \n")
        str += ("A=M \n")
        str += ("M=D \n")
        # Inc. Stack
        str += ("@SP \n")
        str += ("M=M+1 \n")
        self.counter +=1
        return str

    def write_eq(self):
        str = ""
        str += ("// eq \n")
        # Pop Into D
        str += ("@SP \n")
        str += ("M=M-1 \n")
        str += ("A=M \n")
        str += ("D=M \n")
        # Subtract x- y
        str += ("@SP \n")
        str += ("M=M-1 \n")
        str += ("A=M \n")
        str += ("D=M-D \n")
        # Compare
        str += ("@True_{} \n".format(self.counter))
        str += ("D;JEQ \n")
        str += ("D=0 \n")
        str += ("@Then_{} \n".format(self.counter))
        str += ("0;JMP \n")
        str += ("(True_{}) \n".format(self.counter))
        str += ("D=-1 \n")
        str += ("(Then_{}) \n".format(self.counter))
        # Push D (result of comparison) onto stack
        str += ("@SP \n")
        str += ("A=M \n")
        str += ("M=D \n")
        # Inc. Stack
        str += ("@SP \n")
        str += ("M=M+1 \n")
        self.counter +=1
        return str

'''
 Passing parameters from the caller to the called subroutine
m Saving the state of the caller before switching to execute the called subroutine
m Allocating space for the local variables of the called subroutine
m Jumping to execute the called subroutine
m Returning values from the called subroutine back to the caller
m Recycling the memory space occupied by the called subroutine, when it returns
m Reinstating the state of the caller
m Jumping to execute the code of the caller immediately following the spot where
we left it
'''

import sys
import pprint
import os
if __name__ == "__main__":
    if(".vm" in sys.argv[1]):
        #single file
        lex = Lexer(sys.argv[1])
        parser = Parser(lex.process())
        writer = CodeWriter()
        name = os.path.basename(sys.argv[1])
        writer.set_filename(name[0:-3] + ".asm")
        writer.write_init()
        while(parser.hasMoreCommands()):
            parser.advance()
            ct = parser.command_type() 
            if(ct == "C_ARITHMETIC"):
                writer.write_arithmetic(parser.current_command[0])
            elif(ct in ["C_PUSH", "C_POP"]):
                writer.write_push_pop(parser.current_command[0], parser.arg1(), parser.arg2())
            elif(ct == "C_LABEL"):
                writer.write_label(parser.arg1())
            elif(ct == "C_GOTO"):
                writer.write_goto(parser.arg1())
            elif(ct == "C_IF"):
                writer.write_if(parser.arg1())
            elif(ct == "C_CALL"):
                writer.write_call(parser.arg1(), parser.arg2())
            elif(ct == "C_FUNCTION"):
                writer.write_function(parser.arg1(), parser.arg2())
            elif(ct == "C_RETURN"):
                writer.write_return()
        writer.close()