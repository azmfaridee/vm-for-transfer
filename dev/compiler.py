#!/usr/bin/python

import sys

if __name__ == "__main__":
    try:
        if len(sys.argv) < 3:
            print "Usage: python compiler.py t1x.file output.vm"
            exit(1)
    except:
        pass

