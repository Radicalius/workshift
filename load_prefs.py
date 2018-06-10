import sys, requests,getpass,re, os, traceback

def load_prefs(user, pswd, house):

	output = ""

	try:
		days = ["M|T|W|Th|F|S|Su","M","T","W","Th","F","S","Su"]

		# Load variables from config file
		config = {}
		conf = open("config"+os.sep+"config.cfg","r")
		for line in conf:
			if ";" in line:
				vals = line.split(";")
				config[vals[0].strip()] = vals[1].strip()

		def convert_time(time):
			try:
				if time.endswith("am"):
					t = time.split(" ")[0]
					return t if t!="24" else "12"
				else:
					return str(int(time.split(" ")[0])%12 + 12)
			except:
				return "*"

		try:
			login = requests.post("https://workshift.bsc.coop/{0}/admin/index.php".format(house), data={"officer_name":user,"officer_passwd":pswd})
		except:
			return "<font color=#FF0000>Unable to Connect to BSC Server<br/>Check your internet connection and try again<br/>Not Yet Synced</font>"

		if login.status_code != 200:
			return "<font color=#FF0000>Unable to Connect to BSC Server<br/>Check the availability of workshift.bsc.org and try again<br/>Not Yet Synced</font>"

		cookies = login.cookies

		names = []
		name_list = requests.get("https://workshift.bsc.coop/{0}/admin/show_prefs.php".format(house),cookies=cookies).text
		for line in name_list.split("\n"):
			if line.startswith("<OPTION>"):
				names.append(line.replace("<OPTION>",""))

		if names[0] == "":
			return "<font color=#FF0000>Unable to Connect to BSC Server<br/>Check your credentials and try again<br/>Not Yet Synced</font color=#FF0000>"
			sys.exit(2)

		shifts = open(config["DATA"] + os.sep + "shifts.csv","w")

		shift_table = requests.get("https://workshift.bsc.coop/{0}/admin/master_shifts.php".format(house),cookies=cookies).text
		table = shift_table.split("""<table id="bodytable" cellspacing='0'>\n<thead>""")[1].split("</tbody></table>")[0]
		for entry in table.split("\n"):
			values = entry.split("value=")
			line = [re.split("""[>'"]""", e)[1] for e in values if len(e) > 0][1:]
			if len(line) > 1:
				line[0] = line[0].strip().replace("&#039;","")
				shifts.write(", ".join([line[0],"|".join([days[i-2] for i in range(2,10) if line[i]!="XXXXX"]), convert_time(line[10]), convert_time(line[11]), line[1], "1", line[12]]) + "\n")

		people = open(config["DATA"] + os.sep + "people.txt","w")

		for name in names:
			prefs = []
			pref_list = requests.get("https://workshift.bsc.coop/{0}/admin/show_prefs.php".format(house),cookies=cookies, params={"person":name}).text
			for line in pref_list.split("\n"):
				g = line.split("<td class='td1'>")
				if len(g) > 1:
					pref = g[1].split("<")[0]
					job = line.split("<td class='td0'>")[1].split("<")[0]
					prefs.append((job,pref))

			scheds = ""
			try:
				sched_table = pref_list.split("<tr><td></td>")[1].split("</table>")[0]
				x = 8
				for char in sched_table:
					if char in ["+","-","x"]:
						scheds+=char
						x += 1
					if char == "&" or char == "?":
						scheds+=" "
						x += 1
					if x == 24:
						scheds+="\n"
						x = 8

				if x!=8:
					scheds+=(24-x)*' '+"\n"

				people.write(name+"\n")
				people.write("5"+"\n")
				people.write(scheds)
				for i in prefs:
					people.write(i[0].strip().replace("&#039;","")+" = "+i[1]+"\n")
				people.write("[END]\n")
			except:
				pass
	except:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		return exc_type, exc_value, exc_traceback

	return "<font color=#00FF00>Sync Successful</font>"

if __name__ == "__main__":
	print (load_prefs(sys.argv[1], sys.argv[2],sys.argv[3]))
