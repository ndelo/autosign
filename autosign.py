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

	# load CSR from stdin
	csr_from_stdin = sys.stdin.read()
	csr = load_certificate_request(FILETYPE_PEM, csr_from_stdin)

	# NOTE: Ideally we could filter by OID number, but OpenSSL.crypto.X509Extension 
	# doesn't give us the extension's raw OID, and the shortname field returns "UNDEF", 
	# so we access the CSR extension requests by their index
	
	extensions = csr.get_extensions()
	pp_uuid = extensions[0].get_data()[2:].lower().strip()
	pp_cloudplatform = extensions[1].get_data()[2:].lower().strip()
	
	# read in secrets file
	config_file = '/opt/puppetlabs/autosign/config.yml'
	
	f = open(config_file)
	secrets = yaml.safe_load(f)
	f.close()

	# check vsphere for a host mathing pp_uuid extension request
	if pp_cloudplatform == "vmware":
		
		service_instance = SmartConnect(host=secrets['vsphere']['api'], user=secrets['vsphere']['user'], pwd=secrets['vsphere']['password'], sslContext=context)
		atexit.register(Disconnect, service_instance)

		search_index = service_instance.content.searchIndex
		vm = search_index.FindByUuid(None, pp_uuid, True, False)

		if vm == None:	
			exit(1)
		else:
			# check that the hostname on the cert matches the hostname in vshpere 
			if vm.guest.hostName.lower() == sys.argv[1]:
				exit(0)
			else:
				exit(1)
	# check aws for same
	elif cloud_platform == "aws":
		## nothing here yet
	else:
		exit(1)

if __name__ == "__main__":
    main()
