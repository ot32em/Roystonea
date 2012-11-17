'''
    usage:
        python kill_ps.py n1 n2 n3, ... n10

        it will kill process with process id = n1, n2, ... n10
'''

import sys
numbers = list()
for ar in sys.argv:
    try:
        a = int(ar)
        numbers.append(a)
    except ValueError:
        continue

import pexpect
for n in numbers:
    pexpect.run("kill -9 %i" % n )
