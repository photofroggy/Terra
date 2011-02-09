#!python3

import os
import launch
from terra.misc_lib import clean_files

os.chdir(os.path.dirname(os.path.realpath(__file__)))    

if __name__ == '__main__':
    clean_files()
    launch.main_program('--menu')

# EOF
