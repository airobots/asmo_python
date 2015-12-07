#!/usr/bin/env python

'''
    Run function inside python file
    Author:
        Rony Novianto (rony@ronynovianto.com)
'''

import sys
import os
import re

def main():
    if len(sys.argv) >= 3:
        base_name = os.path.basename(sys.argv[1])
        module_name = re.sub('\.py$', '', base_name)
        module = __import__(module_name, fromlist=[sys.argv[1]])
        function = getattr(module, sys.argv[2])
        function(*sys.argv[3:])
        
if __name__ == '__main__':
    main()
