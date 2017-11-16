import sys, requests,getpass,re

#user = raw_input("Login: ")
#pswd = getpass.getpass("Password: ")
user = "kngworkshift"
pswd = "fifty two pickup"

days = ["M|T|W|Th|F|S|Su","M","T","W","Th","F","S","Su"]

def convert_time(time):
	try:
		if time.endswith("am"):
			t = time.split(" ")[0]
			return t if t!="12" else "24"
		else:
			return str(int(time.split(" ")[0])%12 + 12)
	except:
		return "*"

login = requests.post("https://workshift.bsc.coop/kng/admin/index.php", data={"officer_name":user,"officer_passwd":pswd})
cookies = login.cookies

names = []
name_list = requests.get("https://workshift.bsc.coop/kng/admin/show_prefs.php",cookies=cookies).text
for line in name_list.split("\n"):
	if line.startswith("<OPTION>"):
		names.append(line.replace("<OPTION>",""))

shifts = open("shifts.csv","w")

shift_table = requests.get("https://workshift.bsc.coop/kng/admin/master_shifts.php",cookies=cookies).text
table = shift_table.split("""<table id="bodytable" cellspacing='0'>\n<thead>""")[1].split("</tbody></table>")[0]
for entry in table.split("\n"):
	values = entry.split("value=")
	line = [re.split("""[>'"]""", e)[1] for e in values if len(e) > 0][1:]
	if len(line) > 1:
		line[0] = line[0].strip().replace("&#039;","")
		shifts.write(", ".join([line[0],"|".join([days[i-2] for i in range(2,10) if line[i]!="XXXXX"]), convert_time(line[10]), convert_time(line[11]), line[1], "1"]) + "\n")

people = open("people.txt","w")

for name in names:
	print name
	prefs = []
	pref_list = requests.get("https://workshift.bsc.coop/kng/admin/show_prefs.php",cookies=cookies, params={"person":name}).text
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
			if char == "&":
				scheds+=" "
				x += 1
			if x == 24:
				scheds+="\n"
				x = 8

		people.write(name+"\n")
		people.write("5"+"\n")
		people.write(scheds)
		for i in prefs:
			people.write(i[0].strip().replace("&#039;","")+" = "+i[1]+"\n")
		people.write("[END]\n")
	except:
		pass
