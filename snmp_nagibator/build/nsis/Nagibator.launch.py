#!python3.3
import sys, os
scriptdir, script = os.path.split(__file__)
pkgdir = os.path.join(scriptdir, 'pkgs')
sys.path.insert(0, pkgdir)
os.environ['PYTHONPATH'] = pkgdir + os.pathsep + os.environ.get('PYTHONPATH', '')

def excepthook(etype, value, tb):
    "Write unhandled exceptions to a file rather than exiting silently."
    import traceback
    with open(os.path.join(scriptdir, script+'.log'), 'w') as f:
        traceback.print_exception(etype, value, tb, file=f)
sys.excepthook = excepthook

from nagibator import main
main()
