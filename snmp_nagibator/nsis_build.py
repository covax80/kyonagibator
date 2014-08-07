import os
import nsist


distrs_dir = os.path.dirname(os.path.abspath(__file__))

os.system('delete /Q build')

nsist.main(['installer.cfg'])

