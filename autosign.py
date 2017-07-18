import sys
import ssl
import atexit
import boto3.ec2
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import OpenSSL.crypto
from OpenSSL.crypto import load_certificate_request, FILETYPE_PEM
import yaml

def main():

	puppet_node = sys.argv[1].lower()[:sys.argv[1].lower().index('.')]
	config_file = '/opt/puppetlabs/autosign/config.yml'

	# load CSR from stdin
	csr_from_stdin = sys.stdin.read()
	csr = load_certificate_request(FILETYPE_PEM, csr_from_stdin)

	# NOTE: Ideally we could filter by OID number, but OpenSSL.crypto.X509Extension 
	# doesn't give us the extension's raw OID, and the shortname field returns "UNDEF", 
	# so we access the CSR extension requests by their index
	
	extensions = csr.get_extensions()
	node_id = extensions[0].get_data()[2:].lower().strip()
	cloud_platform = extensions[1].get_data()[2:].lower().strip()

	# read in config file for api calls
	f = open(config_file)
	secrets = yaml.safe_load(f)
	f.close()
	
	if cloud_platform == "vmware":	

		# disable SSL certificate verification for self-signed certificates on VSphere server
		context = ssl.SSLContext(ssl.PROTOCOL_TLSv1) 
		context.verify_mode = ssl.CERT_NONE 

		service_instance = SmartConnect(host=secrets['vsphere']['vsphere_server'], user=secrets['vsphere']['user'], pwd=secrets['vsphere']['password'], sslContext=context)
		atexit.register(Disconnect, service_instance)

		search_index = service_instance.content.searchIndex

		vm = search_index.FindByUuid(None, node_id, True, False)			
		
		if vm == None:
        		exit(1)
		else:
			# check that the incoming hostname on the cert matches the hostname in vshpere 
			vm_name = vm.guest.hostName.lower()

			if vm_name.endswith('.princeton.edu'):
				vm_name = vm_name[:vm_name.index('.')]

			if vm_name == puppet_node:
				exit(0)
			else:
				exit(1)

	elif cloud_platform == "aws":
		
		# check that the incoming name on the cert matches the 'Name' tag value on the ec2 instance
		session = boto3.Session(aws_access_key_id=secrets['aws']['access_key_id'],aws_secret_access_key=secrets['aws']['secret_access_key'],region_name=secrets['aws']['region'])
		ec2 = session.resource('ec2')
		instance = ec2.Instance(node_id)
		
		for tag in instance.tags:
			if tag["Key"] == 'Name':
				instance_name = tag["Value"].lower()
	
		if instance_name == puppet_node:
			exit(0)
		else:
			exit(1)
	
	else:
		exit(1)

if __name__ == "__main__":
    main()
