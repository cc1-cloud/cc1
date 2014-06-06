#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print 'Usage ./manage.py <manager> <args>'
        sys.exit(1)

    # cc1dir = os.path.abspath(os.path.dirname(__file__))
    # sys.path.append(os.path.join(cc1dir, sys.argv[1]))

    sys.path.append("/etc/cc1/%s/" % sys.argv[1])

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "%s.settings" % sys.argv[1])

    from django.core.management import execute_from_command_line
    args = sys.argv[:]
    args.pop(1)

    execute_from_command_line(args)
