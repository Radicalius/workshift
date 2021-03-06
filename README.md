## Installation
* Download Latest release from https://github.com/Radicalius/workshift/releases
* Extract zip file
* Download Python  2.7.0 <= version < 3.0.0 from https://www.python.org/downloads/.  (For Max OSX and *nix OS it will already be installed)
* If installing on OSX or *nix, open a terminal and switch to the directory of the extracted files using: 

	```cd [full/path/to/files]```.
    
	Then run autoconfig.sh as root:
    
    ```
    # fedora
    su
    bash autoconfig.sh
    
    # ubuntu
    sudo bash autoconfig.sh
    ```
    The script will guide you in configuring Sorting Hat.
    
    Alternatively, If you are using Windows or the script fails, you will need to fill out the config file manually:
    ```
    Sorting Hat Configuration File

	PYTHON: [full/path/to/python/binary]                 
	DATA: [path/to/data/folder] (default: data)
	CERTIFICATE: [path/to/ssl/certificate] (see below)
	PORT: 443
	```
    
    If setting up a server, you can host it on https by providing an openssl key (.pem file).  This will encrypt the data transferred between server and client, protecting it from wireless network snooping.  On linux, a keypair can be generated by running:
    
    ```
    openssl req -new -x509 -days 365 -nodes -out cert.pem -keyout cert.pem
    ``` 
## Starting the Program
* Run server.py.  On OSX/*nix, open a terminal and change to the Sorting Hat installation directory.  Then execute

	``` nohup python server.py > /dev/null &```
    
    If hosting on a port below 8000, you will have to run this as root.
   
   	On Windows, open the install directory in file explorer and double click on server.py
    
* Using your favorite webrowser, navigate to one of the following addresses:
	1. http://localhost	
	2. http://localhost: [PORT]
	3. https://localhost
	4. https://localhost: [PORT]