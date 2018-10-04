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

        # Sys.vmで利用する
        tmp = None

        #ディレクトリ内のvmファイルをリストで取得する
        for file in os.listdir(self.dir_path):
            file_path = os.path.join(dir_path,file)
            file_name, file_ext = os.path.splitext(file)
            if file_ext == '.vm':
                vm_files.append(file_path)

            # 次のif文で利用
            if (file_name + file_ext) == 'Sys.vm':
                tmp = file_path

        # もしSys.vmがあるのならば先頭にする
        if tmp:
            vm_files.remove(tmp)
            vm_files.insert(0,tmp)

        for vm_file in vm_files:

            # スタティック変数の命名にvmの関数名が必要
            file = os.path.basename(vm_file)
            file_name, file_ext = os.path.splitext(file)

            # lavelの命名規則に利用
            function_name = None

            with open(vm_file) as vm:
                for vm_line in vm:
                    command,arg1,arg2,command_type = self.parser.parser(vm_line)

                    if command:
                        if command_type == 'C_ARITHMETRIC':
                            self.codewriter.write_arithmetric(dir_path,dirname,command,arg1,arg2)
                        if command_type == 'C_POP' or command_type == 'C_PUSH':
                            self.codewriter.write_push_pop(dir_path,dirname,command,arg1,arg2,file_name)
                        if command == 'if-goto':
                            self.codewriter.write_if(dir_path,dirname,command,arg1,arg2,function_name)
                        if command == 'goto':
                            self.codewriter.write_goto(dir_path,dirname,command,arg1,arg2,function_name)
                        if command == 'function':
                            self.codewriter.write_function(dir_path,dirname,command,arg1,arg2)
                            # lavelの生成に利用するので関数名を取得する
                            function_command, function_name, function_arg = vm_line.split()
                        if command == 'call':
                            self.codewriter.write_call(dir_path,dirname,command,arg1,arg2)
                        if command == 'label':
                            self.codewriter.write_label(dir_path,dirname,command,arg1,arg2,function_name)
                        if command == 'return':
                            self.codewriter.write_return(dir_path,dirname,command,arg1,arg2)
                            function_name = None

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
            # subと処理はほとんど同じ
            if command == 'add':
                f.write('@SP\n')
                f.write('A=M-1\n')
                f.write('D=M\n') # D=y
                f.write('A=A-1\n')
                f.write('M=D+M\n')
                # SPの更新
                self.write_SP_minus(f)

            if command == 'sub':
                f.write('@SP\n')
                f.write('A=M-1\n')
                f.write('D=M\n') # D=y
                f.write('A=A-1\n')
                f.write('M=M-D\n') #addと処置がちがうところ
                # SPの更新
                self.write_SP_minus(f)

            #間違ってるので書き直し
            if command == 'neg':
                f.write('@SP\n')
                f.write('A=M-1\n')
                f.write('M=-M\n') # y=-y

            if command == 'and':
                f.write('@SP\n')
                f.write('A=M-1\n')
                f.write('D=M\n') # D=y
                f.write('A=A-1\n')
                f.write('M=D&M\n')
                # SPの更新
                self.write_SP_minus(f)

            if command == 'or':
                f.write('@SP\n')
                f.write('A=M-1\n')
                f.write('D=M\n') # D=y
                f.write('A=A-1\n')
                f.write('M=D|M\n')
                # SPの更新
                self.write_SP_minus(f)

            if command == 'not':
                f.write('@SP\n')
                f.write('A=M-1\n')
                f.write('M=!M\n')

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
                f.write('D;JLT\n') #eqとltと処理が違うのはここ
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

            # eq lt と処理が同じなのでまとめられそう。違うのはif文だけ
            if command == 'gt':
                f.write('@SP\n')
                f.write('A=M-1\n')
                f.write('D=M\n')
                f.write('A=A-1\n')
                f.write('D=M-D\n')
                f.write('@J_TRUE{}\n'.format(self.lavel_count))
                f.write('D;JGT\n') #eqとltと処理が違うのはここ
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

    def write_push_pop(self,dir_path,dirname,command,arg1,arg2,file_name):
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

                # local argument this thatはラベルが違うだけなのでもっとまとめられそう
                if arg1 == 'local':
                    f.write('@'+str(arg2)+'\n')
                    f.write('D=A\n')
                    f.write('@LCL\n')
                    f.write('A=D+M\n') # A = LCL_base + arg2
                    f.write('D=M\n') # D = Ram[LCL_base + arg2]
                    f.write('@SP\n')
                    f.write('A=M\n')
                    f.write('M=D\n')
                    # SPの更新
                    self.write_SP_plus(f)

                if arg1 == 'argument':
                    f.write('@'+str(arg2)+'\n')
                    f.write('D=A\n')
                    f.write('@ARG\n')
                    f.write('A=D+M\n') # A = ARG_base + arg2
                    f.write('D=M\n') # D = Ram[ARG_base + arg2]
                    f.write('@SP\n')
                    f.write('A=M\n')
                    f.write('M=D\n')
                    # SPの更新
                    self.write_SP_plus(f)

                if arg1 == 'this':
                    f.write('@'+str(arg2)+'\n')
                    f.write('D=A\n')
                    f.write('@THIS\n')
                    f.write('A=D+M\n') # A = ARG_base + arg2
                    f.write('D=M\n') # D = Ram[ARG_base + arg2]
                    f.write('@SP\n')
                    f.write('A=M\n')
                    f.write('M=D\n')
                    # SPの更新
                    self.write_SP_plus(f)


                if arg1 == 'that':
                    f.write('@'+str(arg2)+'\n')
                    f.write('D=A\n')
                    f.write('@THAT\n')
                    f.write('A=D+M\n') # A = THAT_base + arg2
                    f.write('D=M\n') # D = Ram[THAT_base + arg2]
                    f.write('@SP\n')
                    f.write('A=M\n')
                    f.write('M=D\n')
                    # SPの更新
                    self.write_SP_plus(f)

                if arg1 == 'temp':
                    f.write('@'+str(arg2)+'\n')
                    f.write('D=A\n')
                    f.write('@5\n') #R5?
                    f.write('A=D+A\n') # A = 5 + arg2
                    f.write('D=M\n') # D = Ram[5 + arg2]
                    f.write('@SP\n')
                    f.write('A=M\n')
                    f.write('M=D\n')
                    # SPの更新
                    self.write_SP_plus(f)

                if arg1 == 'pointer':
                    f.write('@'+str(arg2)+'\n')
                    f.write('D=A\n')
                    f.write('@3\n') #R3?
                    f.write('A=D+A\n') # A = 3 + arg2
                    f.write('D=M\n') # D = Ram[3 + arg2]
                    f.write('@SP\n')
                    f.write('A=M\n')
                    f.write('M=D\n')
                    # SPの更新
                    self.write_SP_plus(f)

                if arg1 == 'static':
                    #f.write('@'+str(arg2)+'\n')
                    #f.write('D=A\n')
                    #f.write('@16\n')
                    #f.write('A=D+A\n') # A = 16 + arg2
                    #f.write('D=M\n') # D = Ram[16 + arg2]
                    #f.write('@SP\n')
                    #f.write('A=M\n')
                    #f.write('M=D\n')
                    f.write('@' + file_name + '.' + arg2 + '\n')
                    f.write('D=M\n')
                    f.write('@SP\n')
                    f.write('A=M\n')
                    f.write('M=D\n')
                    # SPの更新
                    self.write_SP_plus(f)

            if command == 'pop':
                # local argument this thatはラベルが違うだけなのでもっとまとめられそう
                if arg1 == 'local':
                    f.write('@'+str(arg2)+'\n')
                    f.write('D=A\n')
                    f.write('@LCL\n')
                    f.write('D=D+M\n')
                    f.write('@R5\n') # 後のtempに支障をきたさない？
                    f.write('M=D\n') #R[5] = LCL_base + arg2
                    f.write('@SP\n')
                    f.write('A=M-1\n')
                    f.write('D=M\n')
                    f.write('@R5\n')
                    f.write('A=M\n')
                    f.write('M=D\n')
                    # SPの更新
                    self.write_SP_minus(f)

                # localとラベルが違うだけ。もっと短くコードができそう。
                if arg1 == 'argument':
                    f.write('@'+str(arg2)+'\n')
                    f.write('D=A\n')
                    f.write('@ARG\n')
                    f.write('D=D+M\n')
                    f.write('@R5\n')
                    f.write('M=D\n') #Ram[5] = base_arg + arg2
                    f.write('@SP\n')
                    f.write('A=M-1\n')
                    f.write('D=M\n') #D = stack top value
                    f.write('@R5\n')
                    f.write('A=M\n')
                    f.write('M=D\n')
                    # SPの更新
                    self.write_SP_minus(f)

                if arg1 == 'this':
                    f.write('@'+str(arg2)+'\n')
                    f.write('D=A\n')
                    f.write('@THIS\n')
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

                if arg1 == 'that':
                    f.write('@'+str(arg2)+'\n')
                    f.write('D=A\n')
                    f.write('@THAT\n')
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

                if arg1 == 'temp':
                    f.write('@'+str(arg2)+'\n')
                    f.write('D=A\n')
                    f.write('@5\n') #R5?
                    f.write('D=D+A\n') #ここthatと違う
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

                if arg1 == 'pointer':
                    f.write('@'+str(arg2)+'\n')
                    f.write('D=A\n')
                    f.write('@3\n') #R3?
                    f.write('D=D+A\n') #ここthatと違う
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

                if arg1 == 'static':
                    # これXXX.jで作成するラベルはeqとかで作成したやつとかぶらない？
                    # 結局static変数ってなによ?
                    #f.write('@'+str(arg2)+'\n')
                    #f.write('D=A\n')
                    #f.write('@16\n')
                    #f.write('D=D+A\n') #ここthatと違う
                    #f.write('@R5\n')
                    #f.write('M=D\n')
                    #f.write('@SP\n')
                    #f.write('A=M-1\n')
                    #f.write('D=M\n')
                    #f.write('@R5\n')
                    #f.write('A=M\n')
                    #f.write('M=D\n')
                    f.write('@SP\n')
                    f.write('A=M-1\n')
                    f.write('D=M\n')
                    f.write('@' + file_name + '.' + arg2 + '\n')
                    f.write('M=D\n')
                    # SPの更新
                    self.write_SP_minus(f)

    def write_SP_plus(self,f):
            f.write('@SP\n')
            f.write('M=M+1\n')

    def write_SP_minus(self,f):
            f.write('@SP\n')
            f.write('M=M-1\n')

    def write_label(self,dir_path,dirname,command,arg1,arg2,function_name):
        with open(dir_path + dirname +'.asm','a') as f:
            if function_name:
                f.write('(' + function_name +'$' + arg1 + ')\n')
            else:
                f.write('('+ arg1 +')\n')

    def write_goto(self,dir_path,dirname,command,arg1,arg2,function_name):
        with open(dir_path + dirname +'.asm','a') as f:
            if function_name:
                f.write('@' + function_name + '$' + arg1 + '\n')
            else:
                f.write('@' + arg1 + '\n')
            f.write('0;JMP\n')

    def write_if(self,dir_path,dirname,command,arg1,arg2,function_name):
        with open(dir_path + dirname +'.asm','a') as f:
            f.write('@SP\n')
            f.write('A=M-1\n')
            f.write('D=M\n')
            # SPの更新
            self.write_SP_minus(f)
            if function_name:
                f.write('@' + function_name + '$' + arg1 + '\n')
            else:
                f.write('@' + arg1 + '\n')
            f.write('D;JNE\n')

    def write_call(self,dir_path,dirname,command,arg1,arg2):
        with open(dir_path + dirname +'.asm','a') as f:
            # pushの関数を再利用できないか？
            # return_addressはreturn_address_関数名でやってみる
            # lavelには.が入ってもよい?

            # push return_address
            return_address_symbol = 'return_address_' + arg1
            f.write('@' + return_address_symbol + '\n')
            f.write('D=A\n')
            f.write('@SP\n')
            f.write('M=D\n')
            self.write_SP_plus(f)
            # push LCL
            f.write('@LCL\n')
            f.write('D=M\n')
            f.write('@SP\n')
            f.write('A=M\n')
            f.write('M=D\n')
            self.write_SP_plus(f)
            # push ARG
            f.write('@ARG\n')
            f.write('D=M\n')
            f.write('@SP\n')
            f.write('A=M\n')
            f.write('M=D\n')
            self.write_SP_plus(f)
            # push THIS
            f.write('@THIS\n')
            f.write('D=M\n')
            f.write('@SP\n')
            f.write('A=M\n')
            f.write('M=D\n')
            self.write_SP_plus(f)
            # push THAT
            f.write('@THAT\n')
            f.write('D=M\n')
            f.write('@SP\n')
            f.write('A=M\n')
            f.write('M=D\n')
            self.write_SP_plus(f)
            # ARG = SP - n -5
            f.write('@' + arg2 + '\n')
            f.write('D=A\n')
            f.write('@5\n')
            f.write('D=D+A\n') # D = n + 5
            f.write('@SP\n')
            f.write('D=M-D\n') # SP-(n+5)
            f.write('@ARG\n')
            f.write('M=D\n')
            # LCL = SP
            f.write('@SP\n')
            f.write('D=M\n')
            f.write('@LCL\n')
            f.write('M=D\n')
            # goto f
            self.write_goto(dir_path,dirname,command,arg1,arg2,arg1)
            # (return-address)
            f.write('(' + return_address_symbol + ')\n')


    def write_function(self,dir_path,dirname,command,arg1,arg2):
        # 関数のラベルはそのまま関数名でOK
        with open(dir_path + dirname +'.asm','a') as f:
            f.write('(' + arg1 + ')' +'\n')
            #　arg2 個のローカル変数を0に初期化する
            # ラベルを使う書き方にしたほうがよい？
        for i in range(0, int(arg2)):
            self.write_push_pop(dir_path,dirname,'push','constant','0',None)
            self.write_push_pop(dir_path,dirname,'pop','local',str(i),None)
            # 実際はローカル変数が代入されたことになるので、SP += 1
            # push pop の最後の操作を無駄にしているので、もっとよくかけるだろこれ。。。。
            with open(dir_path + dirname +'.asm','a') as f:
                self.write_SP_plus(f)

    def write_return(self,dir_path,dirname,command,arg1,arg2):
        with open(dir_path + dirname +'.asm','a') as f:
            # FRAME = LCL
            # OK?
            f.write('@LCL\n')
            f.write('D=M\n')
            f.write('@R13\n') # Ram[13] = FLAME
            f.write('M=D\n')
            # RET = *(FLAME - 5)
            f.write('@5\n')
            f.write('A=D-A\n')
            f.write('D=M\n')
            f.write('@R14\n') # Ram[14] = RET
            f.write('M=D\n')
            # *ARG = pop()
            f.write('@SP\n')
            f.write('A=M-1\n')
            f.write('D=M\n')
            f.write('@ARG\n')
            f.write('A=M\n')
            f.write('M=D\n')
            # SP = ARG + 1
            f.write('@ARG\n')
            f.write('D=M\n')
            f.write('D=D+1\n')
            f.write('@SP\n')
            f.write('M=D\n')
            # THAT = *(FLAME - 1)
            # OK?
            f.write('@R13\n')
            f.write('D=M\n')
            f.write('@1\n')
            f.write('A=D-A\n')
            f.write('D=M\n')
            f.write('@THAT\n')
            f.write('M=D\n')
            # THIS = *(FLAME - 2)
            # OK?
            f.write('@R13\n')
            f.write('D=M\n')
            f.write('@2\n')
            f.write('A=D-A\n')
            f.write('D=M\n')
            f.write('@THIS\n')
            f.write('M=D\n')
            # ARG = *(FLAME - 3)
            # OK?
            f.write('@R13\n')
            f.write('D=M\n')
            f.write('@3\n')
            f.write('A=D-A\n')
            f.write('D=M\n')
            f.write('@ARG\n')
            f.write('M=D\n')
            # LCL = *(FLAME - 4)
            # OK?
            f.write('@R13\n')
            f.write('D=M\n')
            f.write('@4\n')
            f.write('A=D-A\n')
            f.write('D=M\n')
            f.write('@LCL\n')
            f.write('M=D\n')
            # goto RET
            # 途中?続きがある

'''main script start'''
if __name__ == "__main__":
    script, dir_path = argv

    # dir_pathの最後に'/'がなかったら追加する。
    if dir_path[-1] != '/':
        dir_path = dir_path + '/'

    vmt = VMTranslator(dir_path)
    vmt.translater()
