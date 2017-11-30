#!/usr/bin/python

###############################################################################################################################
# Sorting Hat Server
#
# Kingman Workshift Assignment Program
# Version: 1.0.0 Alpha
# Contact: mr.zacharycotton@gmail.com
# Hosts the website for the assignment program
# Usage: python server.py [port]
# Website will be hosted on localhost:[port]
###############################################################################################################################

import BaseHTTPServer,sys, urllib, os,ssl
from BaseHTTPServer import *

# Holds values from config file
config = {}

# Load variables from config file
conf = open("config"+os.sep+"config.cfg","r")
for line in conf:
	if ":" in line:
		vals = line.split(":")
		config[vals[0].strip()] = vals[1].strip()

try:
	port = int(config["PORT"])
except:
	print "Invalid or no Port Specified (Must be integer) Check value listed in config/config.cfg"

# Customize the basic request handler
class SortingHatRequestHandler(BaseHTTPRequestHandler):

	def do_GET(self):
		# method called whenever the server recieves an HTTP GET request.
		# In other words, whenever the website is requested
		# self.wfile is a stream to the client
		# code sent through will appear on their browser
		# self.path is the relative url requested

		# check to see that the requested url is valid
		if self.path in ["/", "/main.js","/res.csv","/shifts.csv","/people.txt"] or self.path.startswith("/query") or self.path.startswith("/sync"):
		
			# Inform the client that the request was successful and we are sending HTML
			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()

			if self.path == "/":

				# send the contents of html/index.html
				self.send_page("html" + os.sep+"index.html")

			elif self.path == "/res.csv":

				# send contents of /data/res.csv (a little hacky :))
				self.send_page(config["DATA"] + os.sep + "res.csv")

			elif self.path == "/shifts.csv":

				# send contents of /data/shifts.csv
				self.send_page(config["DATA"] + os.sep + "shifts.csv")

			elif self.path == "/people.txt":

				# send contents of /data/res.csv (a little hacky :))
				self.send_page(config["DATA"] + os.sep + "people.txt")


			elif self.path.startswith("/query"):   # job request

				# gather argument keys and values
				query_string = self.path.split("?")[1]                              # remove /query?
				args = dict([arg.split("=") for arg in query_string.split("&")])    # key value pairs of query string

				people = open(config["DATA"] + os.sep + "people.txt","w")
				people.write(urllib.unquote(args["people"]))
				people.close()

				shifts = open(config["DATA"] + os.sep + "shifts.csv","w")
				shifts.write(urllib.unquote(args["shifts"]))
				shifts.close()

				output = os.popen(config["PYTHON"] + " algo2.py 2>&1").read()                         # connect and read the output from the algorithym
				output = "<br/>"+output.replace("\n","<br/>")
				self.wfile.write(output)                                            # then send to client

			elif self.path.startswith("/sync"):                                     # user is requesting to grab preferences from bsc.coop

				# extract user and pass
				path = self.path.split("?")[1]
				args = path.split("&")
				user = args[0].split("=")[1]
				pswd = args[1].split("=")[1]
				house = args[2].split("=")[1]

				# run load_prefs script
				os.system(config["PYTHON"] + " load_prefs.py '"+urllib.unquote(user)+"' '"+urllib.unquote(pswd)+"' '"+urllib.unquote(house)+"'")
				self.wfile.write("Finished")

			else:

				# send the contents of html/[path]
				self.send_page("html" + os.sep + self.path) 

		else:

			# Notify the client that the page was not found
			self.send_response(404)
			self.send_header('Content-type', 'text/html')
			self.end_headers()

			# send a human readable error message
			self.wfile.write("<h1>Error 404: Page Not Found</h1><hr/>Check to make sure the URL is valid and try again.")

	def send_page(self,file):
		# send the HTML code contained in file to the client's browser 
		page = open(file, "r")
		contents = page.read()
		self.wfile.write(contents)

# Start Server
server = HTTPServer(("", port), SortingHatRequestHandler)
server.socket = ssl.wrap_socket(server.socket, certfile=config["CERTIFICATE"], server_side=True)
server.serve_forever()
