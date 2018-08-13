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

'''main script start'''
if __name__ == "__main__":
    script, dirname = argv
    vmtranslater = VMtranslator(dirname)
    vmtranslater.vm_translater()
