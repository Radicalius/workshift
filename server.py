#!/usr/bin/python

###############################################################################################################################
# Sorting Hat Server
#
# Kingman Workshift Assignment Program
# Version: 1.0.0 Alpha
# Contact: mr.zacharycotton@gmail.com
# Hosts the website for the assignment program
# Usage: python server.py
###############################################################################################################################

import BaseHTTPServer,sys, urllib, os,ssl
from BaseHTTPServer import *
from subprocess import Popen, PIPE
from load_prefs import load_prefs

# Holds values from config file
config = {}

# Load variables from config file
conf = open("config"+os.sep+"config.cfg","r")
for line in conf:
	if ";" in line:
		vals = line.split(";")
		config[vals[0].strip()] = vals[1].strip()

try:
	if config["PORT"] != "$PORT":
		port = int(config["PORT"])
	else:
		port = int(sys.argv[1])
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
		if self.path in ["/", "/main.js","/res.csv","/shifts.csv","/people.txt","/log.html"] or self.path.startswith("/query") or self.path.startswith("/sync"):

			# Inform the client that the request was successful and we are sending HTML
			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()

			if self.path == "/":

				# send the contents of html/index.html
				self.send_page("html" + os.sep + "index.html")

			elif self.path == "/res.csv":

				# send contents of /data/res.csv (a little hacky :))
				self.send_page(config["DATA"] + os.sep + "res.csv")

			elif self.path == "/shifts.csv":

				# send contents of /data/shifts.csv
				self.send_page(config["DATA"] + os.sep + "shifts.csv")

			elif self.path == "/people.txt":

				# send contents of /data/res.csv (a little hacky :))
				self.send_page(config["DATA"] + os.sep + "people.txt")

			elif self.path == "/log.html":

				# send contents of /data/res.csv (a little hacky :))
				self.send_page(config["DATA"] + os.sep + "log.html")


			elif self.path.startswith("/sync"):                                     # user is requesting to grab preferences from bsc.coop

				# extract user and pass
				path = self.path.split("?")[1]
				args = path.split("&")
				user = args[0].split("=")[1]
				pswd = args[1].split("=")[1]
				house = args[2].split("=")[1]

				# run load_prefs script
				output = load_prefs(urllib.unquote(user), urllib.unquote(pswd), urllib.unquote(house))
				print (output)
				self.wfile.write(output)

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

	def do_POST(self):
		if self.path.startswith("/query"):   # job request

			# gather argument keys and values
			content_len = int(self.headers.getheader('Content-length', 0))
			print (content_len)
			post_body = self.rfile.read(content_len)                            
			args = dict([arg.split("=") for arg in post_body.split("&")])    # key value pairs of query string

			people = open(config["DATA"] + os.sep + "people.txt","w")
			people.write(urllib.unquote(args["people"]))
			people.close()

			shifts = open(config["DATA"] + os.sep + "shifts.csv","w")
			shifts.write(urllib.unquote(args["shifts"]))
			shifts.close()

			inp,output,error = os.popen3(config["PYTHON"] + " algo2.py "+args["gtf"]+" "+args["btf"]) # connect and read the output from the algorithym
			output = "<br/>"+(output.read()+error.read()).replace("\n","<br/>")

			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()
			self.wfile.write(output)                                            # then send to client


	def send_page(self,file):
		# send the HTML code contained in file to the client's browser 
		page = open(file, "r")
		contents = page.read()
		self.wfile.write(contents)

# Start Server
server = HTTPServer(("", port), SortingHatRequestHandler)
if os.path.exists(config["CERTIFICATE"]):
	server.socket = ssl.wrap_socket(server.socket, certfile=config["CERTIFICATE"], server_side=True)
server.serve_forever()
