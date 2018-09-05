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
# 初期値を設定する必要はある?
# このメモリの操作はアセンブラで行っていないが、それもアセンブラにしたほうがよい。
# popからはこれを修正した。
Ram[symboltable['SP']] = 256

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
    def __init__(self):
        pass

    # 作成するasmファイルを初期化する
    # このときRAM[0] = 256 (SP)になるように機械語を出力しておく。
    def set_file_name(self,dir_path,dirname):
        with open(dir_path + dirname + '.asm','w') as f:
            print(dir_path + dirname + '.asm file created.')

            # RAM[0] = 256の設定
            f.write('@256\n')
            f.write('D=A\n')
            memory_address = symboltable['SP']
            f.write('@'+str(memory_address)+'\n')
            f.write('M=D\n')

    def write_arithmetric(self,dir_path,dirname,command,arg1,arg2):
        with open(dir_path + dirname + '.asm','a') as f:
            if command == 'add':
                memory_address_y = Ram[symboltable['SP']] - 1 #stackの先頭は(SP-1)
                asm_code = '@' + str(memory_address_y) +'\n'
                f.write(asm_code)
                f.write('D=M\n')

                memory_address_x = Ram[symboltable['SP']] - 2
                asm_code = '@' + str(memory_address_x) +'\n'
                f.write(asm_code)
                f.write('M=M+D\n')

                # memory操作
                f.write('@0\n')
                f.write('M=M-1\n')

                Ram[symboltable['SP']] -= 1
                Ram[memory_address_x] = int(Ram[memory_address_x]) + int(Ram[memory_address_y]) # Ramの要素がstrになっている。。
                Ram[memory_address_x] = str(Ram[memory_address_x])

            if command == 'sub':
                memory_address_y = Ram[symboltable['SP']] - 1 #yのアドレスは(SP-1)
                asm_code = '@' + str(memory_address_y) +'\n'
                f.write(asm_code)
                f.write('D=M\n')

                memory_address_x = memory_address_y - 1 # xのアドレスは(SP - 2)
                asm_code = '@' + str(memory_address_x) +'\n'
                f.write(asm_code)
                f.write('M=M-D\n')

                f.write('@0\n')
                f.write('M=M-1\n')

                # Ramの操作
                # xの更新
                Ram[memory_address_x] = int(Ram[memory_address_x]) - int(Ram[memory_address_y]) # Ramの要素がstrになっている。。
                Ram[memory_address_x] = str(Ram[memory_address_x])
                # Ram[0]の更新
                Ram[0] -= 1

            if command == 'neg':
                memory_address_y = Ram[symboltable['SP']] - 1 #yのアドレスは(SP-1)
                asm_code = '@' + str(memory_address_y) +'\n'
                f.write(asm_code)
                f.write('M=-M\n')

                Ram[memory_address_y] = - int(Ram[memory_address_y])
                Ram[memory_address_y] = str(Ram[memory_address_y])

            if command == 'and':
                memory_address_x = Ram[symboltable['SP']] - 2
                memory_address_y = Ram[symboltable['SP']] - 1

                x = Ram[memory_address_x]
                y = Ram[memory_address_y]

                # xとyが負数の場合の処理はどうすればよいだろう。。。
                # andの計算
                # pythonはバイナリにせずとも２進数の論理積がとれる
                Ram[memory_address_x] = int(x) & int(y)
                Ram[memory_address_x] = str(Ram[memory_address_x])
                asm_code = '@' + Ram[memory_address_x] +'\n'
                f.write(asm_code)
                f.write('D=A\n')
                asm_code = '@' + str(memory_address_x) +'\n'
                f.write(asm_code)
                f.write('M=D\n')

                # SPの更新
                Ram[symboltable['SP']] = Ram[symboltable['SP']] - 1
                f.write('@0\n')
                f.write('M=M-1\n')

            if command == 'or':
                memory_address_x = Ram[symboltable['SP']] - 2
                memory_address_y = Ram[symboltable['SP']] - 1

                x = Ram[memory_address_x]
                y = Ram[memory_address_y]

                # xとyが負数の場合の処理はどうすればよいだろう。。。
                # andの計算
                # pythonはバイナリにせずとも２進数の論理積がとれる
                # そもそもD | A　やD & A の計算を利用してなくない？
                # SP - 1 の呼び出しにはアセンブラを利用しなくてよいの?
                Ram[memory_address_x] = int(x) | int(y)
                Ram[memory_address_x] = str(Ram[memory_address_x])
                asm_code = '@' + Ram[memory_address_x] +'\n'
                f.write(asm_code)
                f.write('D=A\n')
                asm_code = '@' + str(memory_address_x) +'\n'
                f.write(asm_code)
                f.write('M=D\n')

                # SPの更新
                Ram[symboltable['SP']] = Ram[symboltable['SP']] - 1
                f.write('@0\n')
                f.write('M=M-1\n')

            if command == 'not':
                memory_address_y = Ram[symboltable['SP']] - 1 #yのアドレスは(SP-1)
                D_tmp = ~int(Ram[memory_address_y]) #~で反転するやつ
                #もっときれいにかけるかも。
                if D_tmp >= 0:
                    asm_code = '@' + str(D_tmp) +'\n'
                    f.write(asm_code)
                    f.write('D=A\n')
                else:
                    asm_code = '@' + str(-D_tmp) +'\n'
                    f.write(asm_code)
                    f.write('D=-A\n')

                asm_code = '@' + str(memory_address_y) +'\n'
                f.write(asm_code)
                f.write('M=D\n')

                asm_code = '@' + str(memory_address_y) +'\n'
                f.write(asm_code)
                f.write('M=D\n')

                Ram[memory_address_y] = D_tmp
                Ram[memory_address_y] = str(Ram[memory_address_y])

            # eq lt と処理が同じなのでまとめられそう。違うのはif文だけ
            # JEQなどのjump命令を利用できないか??
            # @0などしなくても@LCLを理解してくれる??
            if command == 'eq':
                SP_address = Ram[symboltable['SP']]

                if Ram[SP_address - 2] == Ram[SP_address -1]:
                    Ram[SP_address - 2] = Ram[SP_address] - 1

                    f.write('@1\n')
                    f.write('D=-A\n')
                else:
                    Ram[SP_address - 2] = 0

                    f.write('@0\n')
                    f.write('D=A\n')

                f.write('@' + str(SP_address-2) + '\n')
                f.write('M=D\n')

                Ram[symboltable['SP']] = Ram[symboltable['SP']] - 1
                f.write('@0\n')
                f.write('M=M-1\n')

            # eq lt と処理が同じなのでまとめられそう。違うのはif文だけ
            if command == 'lt':
                SP_address = Ram[symboltable['SP']]

                if Ram[SP_address - 2] < Ram[SP_address -1]:
                    Ram[SP_address - 2] = Ram[SP_address] - 1

                    f.write('@1\n')
                    f.write('D=-A\n')
                else:
                    Ram[SP_address - 2] = 0

                    f.write('@0\n')
                    f.write('D=A\n')

                f.write('@' + str(SP_address-2) + '\n')
                f.write('M=D\n')

                Ram[symboltable['SP']] = Ram[symboltable['SP']] - 1
                f.write('@0\n')
                f.write('M=M-1\n')

            # eq lt と処理が同じなのでまとめられそう。違うのはif文だけ
            if command == 'gt':
                SP_address = Ram[symboltable['SP']]

                if Ram[SP_address - 2] > Ram[SP_address -1]:
                    Ram[SP_address - 2] = Ram[SP_address] - 1

                    f.write('@1\n')
                    f.write('D=-A\n')
                else:
                    Ram[SP_address - 2] = 0

                    f.write('@0\n')
                    f.write('D=A\n')

                f.write('@' + str(SP_address-2) + '\n')
                f.write('M=D\n')

                Ram[symboltable['SP']] = Ram[symboltable['SP']] - 1
                f.write('@0\n')
                f.write('M=M-1\n')

    def write_push_pop(self,dir_path,dirname,command,arg1,arg2):
        with open(dir_path + dirname +'.asm','a') as f:
            if command == 'push':
                if arg1 == 'constant':
                    # memory操作
                    f.write('@'+str(arg2)+'\n')
                    f.write('D=A\n')
                    memory_address = Ram[symboltable['SP']]
                    f.write('@'+str(memory_address)+'\n')
                    f.write('M=D\n')
                    Ram[memory_address] = arg2

                    # SPの更新
                    Ram[symboltable['SP']] = Ram[symboltable['SP']] + 1
                    f.write('@0\n')
                    f.write('M=M+1\n')
                    # SPの値は本に記載されているようにbase + i番目とできればよかったかな?

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
