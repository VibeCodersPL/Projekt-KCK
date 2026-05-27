import os
import sys
from windows.menu import *

current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..'))

if src_path not in sys.path:
    sys.path.append(src_path)

if __name__ == '__main__':
    Menu().run()