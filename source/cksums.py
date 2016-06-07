import os
import hashlib

def walkdirs(dir):
    for dirpath, dnames, fnames in os.walk(dir):
    	for f in fnames:
    		print("{0}\t{1}".format(f, dirpath))

def listfiles(directory):
    files = os.listdir(directory)
    for f in files:
        cksum = md5(f)
        print(f, "=", cksum)
 
def md5(filename):
    hasher = hashlib.md5()
    with open(filename, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def main():
    directory = input("Enter path: ")
    walkdirs(directory)
    
main()