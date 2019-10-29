#----------------imports-----------------#

import re
import subprocess
from ctypes import *

#--------------Sahil Bisla---------------#
proc_name = "com.tencent.ig"
module_name = "libUE4.so"

maps_file = None
pid = -1

#----------------Definations--------------#
class iovec(Structure):
    _fields_ = [("iov_base",c_void_p),("iov_len",c_size_t)]

libc = CDLL("libc.so")
prvm = libc.process_vm_readv
prvm.argtypes = [c_int, POINTER(iovec), c_ulong, POINTER(iovec), c_ulong, c_ulong]

def getAddressOfModule(modulename):
	address = []
	if maps_file is not None:
		for line in maps_file.readlines():
			page = line.split()
			module = page[len(page) - 1]
			
			if modulename in module:
				address.append(page[0].split('-'))
			
	return address
	
def rpm(address, length):
	local = (iovec*1)()[0]
	remote =  (iovec*1)()[0]
	buf = (c_char*length)()
	
	local.iov_base = cast(byref(buf),c_void_p)
	local.iov_len = length
	remote.iov_base = c_void_p(address)
	remote.iov_len = length
	
	nread = prvm(pid,local,1,remote,1,0)
	
	return nread, buf
	
#--------------Prog Start----------------#
if __name__ == '__main__':
	result = subprocess.getoutput("ps aux | grep " + proc_name + " | awk '{print $2}'")
	pid = int(result.split()[0])
	if pid < 0:
		print("Proccess Not Found!")
		exit()

	print("Proccess Found on PID: ", pid)
	maps_file = open("/proc/" + str(pid) + "/maps", 'r')
	
	address = getAddressOfModule(module_name)
	if len(address) < 1:
		print("Module Not Found!")
		exit()
	
	print("Module ",module_name," Found on BaseAddress: ", address[0][0])
	
	startAddr = int(address[0][0], 16)
	endAddr = int(address[len(address)-1][1], 16)
	
	nread, buf = rpm(startAddr, endAddr - startAddr)
	if nread != -1:
		open("/sdcard/" + module_name, 'wb').write(buf)
		print("Dumping of ",module_name, " Done by Bisla Dumper!")
			
	maps_file.close()