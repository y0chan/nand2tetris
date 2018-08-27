'''
Python Version:
    python3.6

OS:
    OS X El Capitan
    Version: 10.11.6

Usage:
    python 3.6 VMtransfer.py [Directory including .vm file]
    * Don't add last word of path '/'
'''
from sys import argv
import os
import re

'''Initial Setting'''
# lavel:RAM Address
symboltable = {
            'SP':0,
            'LCL':1,
            'ARG':2,
            'THIS':3,
            'THAT':4,
            'SCREEN':16384,
            'KBD':24576
            }
for i in range(0,16):
    key = 'R' + str(i)
    symboltable[key] = i

# RAM
Ram = [0 for w in range(32768)]
# initial RAM setting
Ram[symboltable['SP']] = 256

'''class VMTranslator'''
class VMTranslator(object):
    def __init__(self,dir_path):
        self.dir_path = dir_path
        self.parser = Parser()
        self.codewriter = CodeWriter()

    def translater(self):

        # 引数のディレクトリ名を取得
        #　いらなかったかも。。。。。
        #dirname = self.get_argdirname(self.dir_path)

        # [引数のディレクトリ名.asm]を作成する
        self.codewriter.set_file_name(self.dir_path)

        # ディレクトリ内のvmファイルのリストを取得
        vm_files = []

        #ディレクトリ内のvmファイルをリストで取得する
        for file in os.listdir(self.dir_path):
            file_path = os.path.join(dir_path,file)
            file_name, file_ext = os.path.splitext(file)
            if file_ext == '.vm':
                vm_files.append(file_path)

        for vm_file in vm_files:
            with open(vm_file) as vm:
                for vm_line in vm:
                    command,arg1,arg2,command_type = self.parser.parser(vm_line)

                    if command:
                        if command_type == 'C_ARITHMETRIC':
                            self.codewriter.write_arithmetric(dir_path,command,arg1,arg2)
                        if command_type == 'C_POP' or command_type == 'C_PUSH':
                            self.codewriter.write_push_pop(dir_path,command,arg1,arg2)

    # 引数の最後に/がついているとだめなバグがある。。。
    # いらなかったかも。。
    def get_argdirname(self,dir_path):
        argdirname = os.path.dirname(dir_path)
        return argdirname

'''class Parser'''
class Parser(object):
    def __init__(self):
        pass

    def parser(self,vm_line):
        vm_line = vm_line.rstrip()

        if self.command_descrimination(vm_line):
            command, arg1, arg2 = self.command_parser(vm_line)
            command_type = self.command_type(command)
        else:
            command, arg1, arg2, command_type = None,None,None,None

        return command, arg1, arg2, command_type

    '''vmファイルの一行が与えられ、それがコマンド行かを判別する'''
    '''コマンド行ならばTrueを返す'''
    def command_descrimination(self,vm_line):
        if re.match(r'//',vm_line) or vm_line == '':
            return False
        else:
            return True

    '''コマンド行を分解して、command arg1 arg2を返す'''
    def command_parser(self,vm_line):
        vm_line_array = vm_line.split()
        length_vm_line = len(vm_line_array)

        command = vm_line_array[0]

        if length_vm_line == 1:
            arg1 = None
            arg2 = None
        elif length_vm_line == 2:
            arg1 = vm_line_array[1]
            arg2 = None
        else:
            arg1 = vm_line_array[1]
            arg2 = vm_line_array[2]

        return command, arg1, arg2

    '''command_typeを返す'''
    def command_type(self,command):
        command_arithmetics = [
                                'add',
                                'sub',
                                'neg',
                                'eq',
                                'gt',
                                'lt',
                                'and',
                                'or',
                                'not'
                                ]

        if command in command_arithmetics:
            return 'C_ARITHMETRIC'
        elif command == 'pop':
            return 'C_POP'
        elif command == 'push':
            return 'C_PUSH'

'''class CodeWriter'''
class CodeWriter(object):
    def __init__(self):
        pass

    # 作成するasmファイルを初期化する
    def set_file_name(self,dir_path):
        with open(dir_path + '.asm','w') as f:
            print(dir_path + '.asm file created.')

    def write_arithmetric(self,dir_path,command,arg1,arg2):
        with open(dir_path + '.asm','a') as f:
            if command == 'add':
                memory_address = Ram[symboltable['SP']] - 1 #stackの先頭は(SP-1)
                asm_code = '@' + str(memory_address) +'\n'
                f.write(asm_code)
                f.write('D=M\n')

                memory_address -= 1
                asm_code = '@' + str(memory_address) +'\n'
                f.write(asm_code)
                f.write('M=M+D\n')

                # memory操作
                Ram[symboltable['SP']] -= 1
                memory_address = Ram[symboltable['SP']] - 1
                Ram[memory_address] += Ram[memory_address + 1]


    def write_push_pop(self,dir_path,command,arg1,arg2):
        with open(dir_path + '.asm','a') as f:
                if arg1 == 'constant':
                    # memory操作
                    memory_address = Ram[symboltable['SP']]
                    asm_code = '@' + str(memory_address) + '\n'
                    f.write(asm_code)

                    Ram[memory_address] = arg2
                    f.write('M=0\n')
                    for i in range(0,int(arg2)):
                        f.write('M=M+1\n')

                    Ram[symboltable['SP']] += 1




'''main script start'''
if __name__ == "__main__":
    script, dir_path = argv
    vmt = VMTranslator(dir_path)
    vmt.translater()
