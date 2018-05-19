
import os,sys

filename = os.path.join(os.path.dirname(sys.path[0]), 'tool')
filepath = os.path.join(filename, 'proxy.txt')

print(filepath)