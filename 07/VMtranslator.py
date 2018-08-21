'''
Python Version:
    python3.6

OS:
    OS X El Capitan
    Version: 10.11.6

Usage:
    python 3.6 VMtransfer.py [Directory including .vm file]
'''
from sys import argv
import os
import re

c_arithmetics = [
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

# RAM value
Ram = [0 for w in range(32768)]

# initial RAM setting
Ram[symboltable['SP']] = 256

'''class VMtransfer'''
class VMtranslator(object):
    def __init__(self, dirpath):
        self.dirpath = dirpath

    def vm_translater(self):
        dir_path = self.review_dir_path(self.dirpath)
        vm_files = self.catch_vm_file_list(dir_path)

        '''.asmファイルを作成し書き込んでいく'''
        with open(dir_path  + '.asm', 'w') as asm_file:
            for vm_file in vm_files:
                parse = Parse(vm_file)
                parse.parser()
                asm_file.write(vm_file)
                asm_file.write('\n')

    '''ディレクトリから.vmファイルのリストを取得'''
    '''ファイルリストはフルパスである必要がある'''
    def catch_vm_file_list(self, dirpath):
        vm_files = []

        files = os.listdir(dirpath)
        for file in files:
            name, ext = os.path.splitext(file)
            if ext == '.vm':
                vm_files.append((dirpath + '/' + file))
        return vm_files

    '''ファイルパスの最後に'/'がある場合削除して返す'''
    def review_dir_path(self, dirpath):
        # dirpathの最後が'/'である場合
        if dirpath[-1] == '/':
            dirpath = dirpath[:-1] #  最後の'/'を取る

        return dirpath

'''class Parser'''
class Parse(object):
    def __init__(self,vm_file):
        self.vm_file = vm_file
        self.codewriter = CodeWriter()

    def parser(self):
        with open(self.vm_file) as input:
            for line in input:
                line = line.rstrip()
                if line == '' or re.match(r'//',line):
                    continue
                line_array = line.split(' ')
                line_command_type = self.command_type(line_array[0])
                command = line_array[0]
                # line_arrayの長さが1でなかったら引数があるよ
                if len(line_array) > 1:
                    command_arg1 = line_array[1]
                    command_arg2 = line_array[2]
                # 引数なしの場合
                else:
                    command_arg1 = ''
                    command_arg2 = ''

                # ここまででvmのコマンドと引数はわかったので
                # class CodeWriterでコマンドを返す
                # commandとarg1とarg2を渡す
                if command == 'pop' or command == 'push':
                    asm = self.codewriter.writepushpop(command,command_arg1,command_arg2)
                    print(asm)
                    #print(Ram[symboltable['SP']])
                    #print(Ram[Ram[symboltable['SP']]])


    def command_type(self,command):
        if command in c_arithmetics:
            return 'C_ARITHMETIC'
        elif command == 'push':
            return 'C_PUSH'
        elif command == 'pop':
            return 'C_POP'
        else:
            return 'null'

'''class Parser'''
class CodeWriter(object):
    def __init__(self):
        pass

    def writepushpop(self,command,arg1,arg2):
        asm = []
        if arg1 == 'constant':
            if command == 'push':
                asm.append('@' + str(Ram[symboltable['SP']]))
                SP_number = Ram[symboltable['SP']]

                asm.append('M='+str(arg2))
                Ram[SP_number] = arg2 # メモリに値を入れる

                Ram[symboltable['SP']] += 1 # SPの値を更新する
                return asm


'''main script start'''
if __name__ == "__main__":
    script, dirname = argv
    vmtranslater = VMtranslator(dirname)
    vmtranslater.vm_translater()
