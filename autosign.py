import sys
import boto
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import OpenSSL.crypto
from OpenSSL.crypto import load_certificate_request, FILETYPE_PEM
import yaml
import ssl 
import atexit

def main():
	# disable SSL certificate verification for self-signed certificates on VSphere server
	context = ssl.SSLContext(ssl.PROTOCOL_TLSv1) 
	context.verify_mode = ssl.CERT_NONE 

	# load csr from stdin
	csr_from_stdin = sys.stdin.read()
	csr = load_certificate_request(FILETYPE_PEM, csr_from_stdin)

	# get extension requests
	# NOTE: Ideally we could filter by OID number, but OpenSSL.crypto.X509Extension 
	# doesn't give us the extension's raw OID and the shortname field returns 
	# "UNDEF",  so we access the extensions by their index number
	extensions = csr.get_extensions()
	uuid = extensions[0].get_data()[2:].lower().strip()
	cloud_platform = extensions[1].get_data()[2:].lower().strip()

	f = open('config.yml')
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

if __name__ == "__main__":
    main()