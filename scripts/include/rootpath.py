import os

try:
    ROYSTONEA_ROOT
except NameError:
    ROYSTONEA_ROOT = os.path.normpath( "%s/../.." % os.path.dirname( os.path.abspath(__file__) ))
