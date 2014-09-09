DALI-WebGUI
===========

ABOUT
=====
DALI-WebGui is a user interface for write and execute DALI agent in a Multi-Agent System (MAS).

## Dependencies
* [Flask](http://flask.pocoo.org)
* [Twisted] (http://twistedmatrix.com)

INSTALLATION
============

Pre-installation
---------------
Before installing make sure you have installed python and a MySQL server.

You must also install the dependencies for python project

For example, for the installation on Ubuntu::

	sudo apt-get update

	sudo apt-get update
	sudo apt-get install build-essential autoconf libtool pkg-config libevent-dev python-dev
	sudo apt-get install python-pip python-dev build-essential
	sudo pip install --upgrade pip

	sudo apt-get install python-dev libmysqlclient-dev

	pip install MySQL-python
	pip install Flask
	pip install twisted

	
Installation
---------------
If you are sure you have all the components of the pre-installation, you will not need to install anything else; the only thing to do is create a MySQL database for DALI and import the dump file that is located in the ``utils`` folder. 
Next you'll need only configure the client and the server.


Configuration
===========
For the client side to change the configuration file ``config.js`` in the folder ``src/app/config``, enter the address and port of the server. 
For Example

::

	angular.module('CONSTANTS', [])
		.constant('CONFIG',{
			'url' : 'http://localhost:10000/api/'
		});
	;

To change the server-side configuration file ``properties.cfg`` in the folder ``src\server\conf``, going to fill the various fields of the database and server
src/app/config/config.js
For Example

::

	[Database]
	MYSQL_HOST = localhost
	MYSQL_PORT = 3306
	MYSQL_USER = giustino
	MYSQL_PASSWD = ginogino
	MYSQL_DB = dali

	[Server]
	RootFiles = /src/server/files
	ServerPort = 10000