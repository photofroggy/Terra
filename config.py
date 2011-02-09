#!python3

import os
import Launch
from terra.misc_lib import clean_files

os.chdir(os.path.dirname(os.path.realpath(__file__)))    

if __name__ == '__main__':
    clean_files()
    Launch.main_program('--config')

# EOF