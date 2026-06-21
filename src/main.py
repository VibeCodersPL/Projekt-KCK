import sys
import os
from ui.screens.menu_screen import Menu as CyberTrenerApp
current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..'))

if src_path not in sys.path:
    sys.path.append(src_path)

if __name__ == '__main__':
    CyberTrenerApp().run()