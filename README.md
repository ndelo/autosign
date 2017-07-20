# autosign
Python script for policy-based certificate autosigning in Puppet

For more information about policy-based autosigning, see--
https://docs.puppet.com/puppet/5.0/ssl_autosign.html#policy-based-autosigning

This script looks for 2 attributes to be included in the puppet nodes CSR -- pp_cloudprovider and pp_uuid.

Valid values for pp_cloudprovider are "vsphere" or "aws"
Valid values for pp_uuid are a VMware guests UUID or a AWS EC2 InstanceId.

Script will attempt to match either a VMware UUID or a EC InstanceId with 
a running guest in either infrastructure.

The host's name--passed by puppet as a parameter--must match the VMWare guest name,
or the 'Name' tag of an AWS EC2. 





