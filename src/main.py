from windows.menu import *

import os
import sys

current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..'))

if src_path not in sys.path:
    sys.path.append(src_path)
    


if __name__ == '__main__':
    Menu().run()