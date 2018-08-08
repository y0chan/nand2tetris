'''
Python Version:
    python3.6

OS:
    OS X El Capitan
    Version: 10.11.6

Usage:
    python 3.6 Assembler_Symbol.py filename.asm
'''

from sys import argv
import os.path
import re

'''Class Assembler'''
class Assembler(object):
    def __init__(self, filename):
        self.filename = filename
        self.parse = Parse()
        self.intermediate = Intermediate(self.filename)
        self.symboltable = SymbolTable()

    def assembler(self):
        # class Intermediateでコメントと空行を削除した中間ファイルを作成する
        intermediate_file = self.intermediate.make_intermediate_file()

        # class SymbolTableで作成した中間ファイルからシンボルテーブルを作成する
        self.symboltable.make_symboltable(intermediate_file)

        input = open(intermediate_file, 'r')

        #拡張子.hachのファイル名を作成しopen()する
        name = self.catch_filename(self.filename)
        output = open(name + ".hack",'w')

        #inputから1行ずつ読み込み、バイナリに変換
        #outputにバイナリを書き込んでいく
        while True:
            line = input.readline()
            if not line: break
            code = line[:-1] #line[:-1]で末尾の改行コードを削除
            code_type = self.parse.code_type(code)
            line_bynary = self.parse.change_to_bynary(code, code_type, self.symboltable.symboltable)
            output.write(line_bynary)
        #.asmファイルと.hackファイルをcloseする
        input.close()
        output.close()

    #.asmファイルから拡張子を除いたファイル名を取得する
    def catch_filename(self, filename):
        name, ext = os.path.splitext(filename)
        return name

'''class Parse'''
class Parse(object):
    def __init__(self):
        self.code = Code()

    #codeの種類を解析する
    def code_type(self, code):
        if re.match(r'//', code):
            return 'type_comment'
        elif code == '':
            return 'nullline'
        elif code.count('@'):
            return 'type_A'
        elif code.count('=') or code.count(';'):
            return 'type_C'
        elif code.count('('):
            return 'type_Lavel'
        else:
            return 'error'

    #codeの種類(code_type)によってbybaryの変換方法が違うため、
    #codeの種類(code_type)によって異なるbynaryの変換方法を呼び出しその結果を返す
    def change_to_bynary(self, code, code_type, symboltable):
        if code_type == 'type_comment' or code_type == 'nullline':
            return ''
        elif code_type == 'type_A':
            return self.code.return_type_a_bynary(code, symboltable)
        elif code_type == 'type_C':
            return self.code.return_type_c_bynary(code)
        elif code_type == 'type_Lavel':
            return ''

'''class Code'''
class Code(object):
    def __init__(self):

        #a == 0 のときのC命令のbynaryを格納するdict
        self.c_code_dict_a0 = {
            '0':'101010',
            '1':'111111',
            '-1':'111010',
            'D':'001100',
            'A':'110000',
            '!D':'001101',
            '!A':'110001',
            '-D':'001111',
            '-A':'110011',
            'D+1':'011111',
            'A+1':'110111',
            'D-1':'001110',
            'A-1':'110010',
            'D+A':'000010',
            'D-A':'010011',
            'A-D':'000111',
            'D&A':'000000',
            'D|A':'010101'
        }

        #a == 1 のときのC命令のbynaryを格納するdict
        self.c_code_dict_a1 = {
            'M':'110000',
            '!M':'110001',
            '-M':'110011',
            'M+1':'110111',
            'M-1':'110010',
            'D+M':'000010',
            'D-M':'010011',
            'M-D':'000111',
            'D&M':'000000',
            'D|M':'010101'
        }

        #C命令のdestのbynaryを格納するdict
        self.c_code_dict_dest = {
            '':'000',
            'M':'001',
            'D':'010',
            'MD':'011',
            'A':'100',
            'AM':'101',
            'AD':'110',
            'AMD':'111'
        }

        #C命令のjumpのbynaryを格納するdict
        self.c_code_dict_jump = {
            '':'000',
            'JGT':'001',
            'JEQ':'010',
            'JGE':'011',
            'JLT':'100',
            'JNE':'101',
            'JLE':'110',
            'JMP':'111'
        }

        self.symboltable = SymbolTable()

    #A命令(code_type == 'type_A')のbynaryを返す
    def return_type_a_bynary(self, code, symboltable):
        decimal_number = code.split('@')[1] #@以降の文字列を抽出
        if symboltable.get(decimal_number): #もしラベルだったらの処理
            decimal_number = symboltable[decimal_number]

        bynary = format(int(decimal_number), 'b').zfill(16)
        return bynary + '\n'

    #C命令(code_type == 'type_C')のbynaryを返す
    def return_type_c_bynary(self, code):
        if code.count('='):
            dest_code, comp_code = code.lstrip().split('=') # .lstrip()で先頭に空白がある場合削除
            dest = self.c_code_dict_dest[dest_code]
            jump = self.c_code_dict_jump['']
        elif code.count(';'):
            comp_code, jump_code = code.lstrip().split(';') # .lstrip()で先頭に空白がある場合削除
            dest = self.c_code_dict_dest['']
            jump = self.c_code_dict_jump[jump_code]

        a, comp = self.return_type_c_comp_bynary(comp_code)
        c_bynary = '111' + a + comp + dest + jump + '\n'
        return c_bynary

    #C命令のaの値とcompのbynaryを返す
    def return_type_c_comp_bynary(self,comp_code):
        if self.c_code_dict_a0.get(comp_code):
            a = '0'
            comp = self.c_code_dict_a0[comp_code]
        elif self.c_code_dict_a1.get(comp_code):
            a = '1'
            comp = self.c_code_dict_a1[comp_code]

        return a, comp

'''class SymbolTable'''
class SymbolTable(object):
    def __init__(self):
        self.symboltable = {
            'SP':'0',
            'LCL':'1',
            'ARG':'2',
            'THIS':'3',
            'THAT':'4',
            'SCREEN':'16384',
            'KBD':'24576'
        }
        for i in range(0,16):
            key = 'R' + str(i)
            self.symboltable[key] = str(i)

    def make_symboltable(self, filename):
        self.check_lavel(filename)
        self.check_variable(filename)

    def check_lavel(self, filename):
        file = open(filename, 'r')
        line_count = -1

        while True:
            line = file.readline()
            if not line: break
            line = line[:-1]
            #　A命令かC命令ならばline_countを+1する
            if line.count('@') or line.count('=') or line.count(';'):
                line_count = line_count + 1

            # ラベルならば line_countのメモリ位置に格納
            if line[0] == '(':
                self.symboltable[line[1:-1]] = str(line_count + 1)

        file.close()

    def check_variable(self, filename):
        file = open(filename, 'r')
        rom_address = 15

        while True:
            line = file.readline()
            if not line:break
            line = line[:-1]
            #もし@X ではじめるならその変数が存在するか確認。ないなら入れる。
            if re.match(r'@', line):
                symbol = line[1:]
                if not self.symboltable.get(symbol) and not symbol.isdigit():
                    self.symboltable[symbol] = str(rom_address + 1)
                    rom_address = rom_address + 1

        file.close()

'''class Intermediate'''
class Intermediate(object):
    def __init__(self, filename):
        self.filename = filename

    def make_intermediate_file(self):
        input = open(self.filename)
        output = open('intermediate.txt', 'w')
        while True:
            line = input.readline()
            if not line: break

            '''lineの処理を場合分けで行う'''
            line = line[:-1] # 改行コードを削除
            if line == '' or re.match(r'//', line):
                continue # 空行ならば次の行の処理へ、先頭が//の場合も
            else:
                line = line.split()[0]#空白やコメントの処理を行う

            output.write(line + '\n')
        input.close()
        output.close()
        return 'intermediate.txt'

'''main script start'''
if __name__ == "__main__":
    script, filename = argv
    asm = Assembler(filename)
    asm.assembler()
