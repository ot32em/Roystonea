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
