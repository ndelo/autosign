import sys
import boto
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import OpenSSL.crypto
from OpenSSL.crypto import load_certificate_request, FILETYPE_PEM
import yaml
import ssl 
import atexit

# disable SSL certificate verification for our self-signed cert
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1) 
context.verify_mode = ssl.CERT_NONE 

# load crs from stdin
csr_from_stdin = sys.stdin.read()
csr = load_certificate_request(FILETYPE_PEM, csr_from_stdin)

extentions = csr.get_extensions()
uuid = extentions[0].get_data()[2:].lower().strip()
cloud_platform = extentions[1].get_data()[2:].lower().strip()

f = open('secrets.yml')
secrets = yaml.safe_load(f)
f.close()

if cloud_platform == "vmware":

	service_instance = SmartConnect(host=secrets['vsphere']['api'], user=secrets['vsphere']['user'], pwd=secrets['vsphere']['password'], sslContext=context)
	atexit.register(Disconnect, service_instance)

	search_index = service_instance.content.searchIndex

	vm = search_index.FindByUuid(None, uuid, True, False)

	if vm == None:	
		exit(1)
	else:
		exit(0)

elif cloud_platform == "aws":
	## to do when we get up and running in aws
	exit(1)

else:
	exit(1)