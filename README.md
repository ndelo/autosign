# autosign
Python script for policy-based certificate autosigning in Puppet.

For more information about policy-based autosigning, see--
https://docs.puppet.com/puppet/5.0/ssl_autosign.html#policy-based-autosigning

This script looks for 2 attributes to be included in the puppet node's CSR -- pp_cloudprovider and pp_uuid.

Valid values for pp_cloudprovider are "vsphere" or "aws"
Valid values for pp_uuid are a VMware guest's UUID or an AWS EC2's InstanceId.

The script checks to see if a host exists in either enviorment that matches both
the host's name (passed to the script by puppet as a parameter) AND that the UUID 
or InstanceId of that host match that listed in the CSR.

If both conditions are met, puppet autosigns the certificate.




