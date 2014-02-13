#!/usr/bin/env python

bytes = range(0,256)
more_bytes = bytearray(bytes)
fh = open('binary_test_file.dat','wb');
fh.write(more_bytes)
fh.close()
