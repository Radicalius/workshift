#!/bin/bash

####################################################################################################################################################################################################################################
# Sorting Hat Autoconfig
# A Script to help set things up on ubuntu
# Usage: bash autoconfig.sh -or- ./autoconfig.sh
# Contact: mr.zacharycotton@gmail.com
####################################################################################################################################################################################################################################

# if config directory doesn't exist, make one
if ! [ -e "config" ]; then
	mkdir config
fi

# generate config file
{
echo -e "Sorting Hat Configuration File\n"

# find python installation
inst=""
for cmd in `whereis "python"` ; do
	if which $cmd > /dev/null; then
		version=`$cmd -c "import sys; print(sys.version_info[0])"`
		if [ $version -eq "2" ]; then
			inst=$cmd
			break
		fi 
	fi
done

# if none was found...
if [ -z $inst ]; then
	echo "Python not found; please install python (2.7.12 <= version < 3.0.0) and try again\nNote: On ubuntu run 'sudo apt-get install python'" >2
	echo "PYTHON; NONE\n"
else
	echo "PYTHON; $inst"
fi

# Defaults:
echo "DATA; `pwd`/data"
echo "CERTIFICATE; `pwd`/config/cert.pem"
echo "PORT; 8000"

} > config/config.cfg

# Check for certificate;
# Create one if not there
if ! [ -f "config/cert.pem" ]; then

	# Check if openssl is installed;
	if ! type openssl > /dev/null; then
		echo "OpenSSL not installed; Please install OpenSSL and try again\nNote: On ubuntu it can be installed by running 'sudo apt-get install openssl'"
	fi

	# Generate RSA certificate
	openssl req -new -x509 -days 365 -nodes -out config/cert.pem -keyout config/cert.pem
fi
