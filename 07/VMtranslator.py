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

'''class VMTranslator'''
class VMTranslator(object):
    def __init__(self,dir_path):
        self.dir_path = dir_path
        self.parser = Parser()
        self.codewriter = CodeWriter()

    def translater(self):

        # 引数のディレクトリ名を取得
        dirname = self.get_argdirname(self.dir_path)

        # [引数のディレクトリ名.asm]を作成する
        self.codewriter.set_file_name(self.dir_path,dirname)

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
                            self.codewriter.write_arithmetric(dir_path,dirname,command,arg1,arg2)
                        if command_type == 'C_POP' or command_type == 'C_PUSH':
                            self.codewriter.write_push_pop(dir_path,dirname,command,arg1,arg2)

    def get_argdirname(self,dir_path):
        tmp_array = dir_path.split('/')
        argdirname = tmp_array[-2]
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

    lavel_count = 0

    def __init__(self):
        pass

    # 作成するasmファイルを初期化する
    # このときRAM[0] = 256 (SP)になるように機械語を出力しておく。
    def set_file_name(self,dir_path,dirname):
        with open(dir_path + dirname + '.asm','w') as f:
            print(dir_path + dirname + '.asm file created.')

    def write_arithmetric(self,dir_path,dirname,command,arg1,arg2):

        with open(dir_path + dirname + '.asm','a') as f:
            if command == 'add':
                f.write('@SP\n')
                f.write('A=M-1\n')
                f.write('D=M\n') # D=y
                f.write('A=A-1\n')
                f.write('M=D+M\n')
                # SPの更新
                self.write_SP_minus(f)

            #if command == 'sub':

            #if command == 'neg':

            #if command == 'and':

            #if command == 'or':

            #if command == 'not':


            # eq lt と処理が同じなのでまとめられそう。
            # lavelが同じになってしまう問題がある
            # eqが２つあったりするとあかん
            if command == 'eq':
                f.write('@SP\n')
                f.write('A=M-1\n')
                f.write('D=M\n')
                f.write('A=A-1\n')
                f.write('D=M-D\n')
                f.write('@J_TRUE{}\n'.format(self.lavel_count))
                f.write('D;JEQ\n')
                f.write('@SP\n') #x≠yの処理
                f.write('A=M-1\n')
                f.write('A=A-1\n')
                f.write('M=0\n')
                f.write('@END{}\n'.format(self.lavel_count)) #ENDへ
                f.write('0;JMP\n')
                f.write('(J_TRUE{})\n'.format(self.lavel_count)) #x=yの処理
                f.write('@SP\n')
                f.write('A=M-1\n')
                f.write('A=A-1\n')
                f.write('M=-1\n')
                f.write('@END{}\n'.format(self.lavel_count)) #ENDへ
                f.write('0;JMP\n')
                f.write('(END{})\n'.format(self.lavel_count))
                self.write_SP_minus(f) #SPの更新

                self.lavel_count += 1

            # eq lt と処理が同じなのでまとめられそう。
            if command == 'lt':
                f.write('@SP\n')
                f.write('A=M-1\n')
                f.write('D=M\n')
                f.write('A=A-1\n')
                f.write('D=M-D\n')
                f.write('@J_TRUE{}\n'.format(self.lavel_count))
                f.write('D;JLT\n')
                f.write('@SP\n') #x≠yの処理
                f.write('A=M-1\n')
                f.write('A=A-1\n')
                f.write('M=0\n')
                f.write('@END{}\n'.format(self.lavel_count)) #ENDへ
                f.write('0;JMP\n')
                f.write('(J_TRUE.{})\n'.format(self.lavel_count)) #x=yの処理
                f.write('@SP\n')
                f.write('A=M-1\n')
                f.write('A=A-1\n')
                f.write('M=-1\n')
                f.write('@END{}\n'.format(self.lavel_count)) #ENDへ
                f.write('0;JMP\n')
                f.write('(END{})\n'.format(self.lavel_count))
                self.write_SP_minus(f) #SPの更新

                self.lavel_count += 1

            # eq lt と処理が同じなのでまとめられそう。違うのはif文だけ
            #if command == 'gt':

    def write_push_pop(self,dir_path,dirname,command,arg1,arg2):
        with open(dir_path + dirname +'.asm','a') as f:
            if command == 'push':
                if arg1 == 'constant':
                    #yにarg2をpush
                    f.write('@'+str(arg2)+'\n')
                    f.write('D=A\n')
                    f.write('@SP\n')
                    f.write('A=M\n')
                    f.write('M=D\n')
                    # SPの更新
                    self.write_SP_plus(f)

            if command == 'pop':
                if arg1 == 'local':
                    asm_code = '@' + str(arg2) + '\n'
                    f.write(asm_code)
                    f.write('D=A\n')
                    f.write('@LCL\n')
                    f.write('D=D+M\n')
                    f.write('@R5\n')
                    f.write('M=D\n')
                    f.write('@SP\n')
                    f.write('A=M-1\n')
                    f.write('D=M\n')
                    f.write('@R5\n')
                    f.write('A=M\n')
                    f.write('M=D\n')
                    # SPの更新
                    self.write_SP_minus(f)

    def write_SP_plus(self,f):
            f.write('@SP\n')
            f.write('M=M+1\n')

    def write_SP_minus(self,f):
            f.write('@SP\n')
            f.write('M=M-1\n')

'''main script start'''
if __name__ == "__main__":
    script, dir_path = argv

    # dir_pathの最後に'/'がなかったら追加する。
    if dir_path[-1] != '/':
        dir_path = dir_path + '/'

    vmt = VMTranslator(dir_path)
    vmt.translater()
