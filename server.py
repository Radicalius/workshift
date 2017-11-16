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

import BaseHTTPServer,sys, urllib, os
from BaseHTTPServer import *

# default port
port = 8000

# get port from args
if len(sys.argv) >= 2:
	try:
		port = int(sys.argv[1])
	except:
		print "Invalid Port Specified: Must be Integer"
		sys.exit(1)                                          # exit code 1 for invalid arguments
else:
	print "usage: python server.py [port]"
	sys.exit(1)

# Customize the basic request handler
class SortingHatRequestHandler(BaseHTTPRequestHandler):

	def do_GET(self):
		# method called whenever the server recieves an HTTP GET request.
		# In other words, whenever the website is requested
		# self.wfile is a stream to the client
		# code sent through will appear on their browser
		# self.path is the relative url requested

		# check to see that the requested url is valid
		if self.path in ["/", "/main.js","/res.csv","/shifts.csv","/people.txt"] or self.path.startswith("/query"):
		
			# Inform the client that the request was successful and we are sending HTML
			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()

			if self.path == "/":

				# send the contents of html/index.html
				self.send_page("index.html")

			elif self.path == "/res.csv":

				# send contents of /data/res.csv (a little hacky :))
				self.send_page("../data/res.csv")

			elif self.path == "/shifts.csv":

				# send contents of /data/shifts.csv
				self.send_page("../data/shifts.csv")

			elif self.path == "/people.txt":

				# send contents of /data/res.csv (a little hacky :))
				self.send_page("../data/people.txt")


			elif self.path.startswith("/query"):   # job request

				# gather argument keys and values
				query_string = self.path.split("?")[1]                              # remove /query?
				args = dict([arg.split("=") for arg in query_string.split("&")])    # key value pairs of query string

				people = open("data/people.txt","w")
				people.write(urllib.unquote(args["people"]))
				people.close()

				shifts = open("data/shifts.csv","w")
				shifts.write(urllib.unquote(args["shifts"]))
				shifts.close()

				output = os.popen("python algo2.py").read()                         # connect and read the output from the algorithym
				output = "<br/>"+output.replace("\n","<br/>")
				self.wfile.write(output)                                            # then send to client

			else:

				# send the contents of html/[path]
				self.send_page(self.path) 

		else:

			# Notify the client that the page was not found
			self.send_response(404)
			self.send_header('Content-type', 'text/html')
			self.end_headers()

			# send a human readable error message
			self.wfile.write("<h1>Error 404: Page Not Found</h1><hr/>Check to make sure the URL is valid and try again.")

	def send_page(self,file):
		# send the HTML code contained in file to the client's browser 
		page = open("html/{0}".format(file), "r")
		contents = page.read()
		self.wfile.write(contents)
		self.wfile.close()

# Start Server
server = HTTPServer(("", port), SortingHatRequestHandler)
server.serve_forever()