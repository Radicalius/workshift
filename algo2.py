###############################################################################################################
#  ____             _   _               _   _       _   
# / ___|  ___  _ __| |_(_)_ __   __ _  | | | | __ _| |_ 
# \___ \ / _ \| '__| __| | '_ \ / _` | | |_| |/ _` | __|
#  ___) | (_) | |  | |_| | | | | (_| | |  _  | (_| | |_ 
# |____/ \___/|_|   \__|_|_| |_|\__, | |_| |_|\__,_|\__|
#                              |___/
#
# Kingman Workshift Assignment Program
# Version 1.0.0
# Contact: mr.zacharycotton@gmail.com
################################################################################################################                  

import sys
import os
import random
from math import ceil

# CONSTANTS #

# Load variables from config file
config = {}
conf = open("config"+os.sep+"config.cfg","r")
for line in conf:
	if ";" in line:
		vals = line.split(";")
		config[vals[0].strip()] = vals[1].strip()

# relative path to directory containing person.txt, and shifts.txt
data_path = config["DATA"]

# shorthands for days of the week.
day_desc = ["M","T","W","Th","F","S","Su"]

# determines how much the desireability of a workshift changes if its assigned
# at a desireable or undesireable time.  Symbols correspond to markers on the preference form
#	+ increased desireability from a preferred time to work
#	- decreased desireability from an undesireable time to work
#  ' ' constant 1 for same desireability for neutral time
#   x constant 0 desireability because the person cannot work at that time
pref_mult = {'+':1.5, '-':0.5, ' ':1.0, 'x':0}

# timeout for stage 1 in iterations
timeout = 100000

# UTILITY FUNCTIONS #

def check_zeros(people):
	# counts the number of assigned workshifts that do not fit into the workshifter's schedule
	z = 0
	for person in people:
		for shift in person.shifts:
			if person.shift_pref(shift) == 0:
				z += 1
	return z

def check_hours(people):
	# counts the number of people who have incorrect total time assignments
	z = 0
	for p in people:
		assigned_hours = sum([w.hours for w in p.shifts])
		if assigned_hours != p.hours:
			z += 1
	return z

def avg_optimality(people):
	# computes average happiness per shift
	score = 0
	total = 0
	for person in people:
		for shift in person.shifts:
			score += person.shift_pref(shift)
			total += 1
	return float(score) / total

def swap(listA,itemA,listB,itemB):
	# itemA in listA and itemB in listB => itemB in listA and itemA in list B
	# >>> a,b = [1,2,3],[4,5,6]
	# >>> swap(a,2,b,5)
	# >>> a
	# [1, 5, 2]
	# >>> b
	# [4, 2, 6]
	listA.remove(itemA)
	listB.append(itemA)
	listB.remove(itemB)
	listA.append(itemB)

def convert_time(time):
	# takes an integer representing a time in 24 hour format
	# converts it to am/pm
	# note that 12:00 am is midnight, and 12:00 pm is noon
	if time < 12:
		return "{0}:00 am".format(time)
	elif time > 12 and time < 24:
		return "{0}:00 pm".format(time-12)
	elif time == 12:
		return "12:00 pm"
	else:
		return "12:00 am"

# CLASSES #

class Person(object):

	def __init__(self, cont):
		self.name = ""
		self.sched = ""               # string representation of schedule: [x|+|-|SPACE] foreach hour.  \n seperate days
		self.sched_nums = {}          # dictionary with keys ([M|T|W|Th|F|S|Su],hour[8-11]) that gives the preference multiplier (x:0,+:1.2,-:0.8,SPACE:1.0) for that time 
		self.shifts = []
		self.hours = 5                # total hours of workshift per week
		self.assigned_hours = 0
		self.pref = ""                # a list of numbers for general preferences per category.  (ie input data)
		self.pref_nums = {}
		self.pref_list = []           # final workshift preference order
		self.locked = None
		self.combos = {}              # dictionary of combinations of workshift that add up to a certain number of hours
		self._load(cont)

	@staticmethod
	def load(file):
		#load all people objects from file
		f = open(file, "r")
		cont = f.read()
		f.close()
		g = cont.split("[END]\n")                 # [END] seperates people entries in the file
		people = [Person(data.split("\n")) for data in g if data!=""]  # Create person object for each entry in file
		return people

	def _load(self,cont):
		# parse person data from text: explicitly invoked by constructor

		# load raw data from file contents
		self.name = cont[0].strip()
		self.hours = int(cont[1].strip())
		self.sched = ("\n".join(cont[2:9]))
		self.pref = cont[9:]

		# parse schedule data
		days = self.sched.split("\n")
		for d,i in zip(day_desc, days):    # d is M|T|W|Th|F|S|Su and i is data for that day
			hour = 8                       # start at 8 am
			for j in i:                    # foreach hour of data
				self.sched_nums[(d,hour)] = pref_mult[j]
				hour+=1

		# parse shift preference data
		for line in self.pref:
			g = line.split(" = ")
			if len(g) > 1:
				self.pref_nums[g[0]] = int(g[1])
		self.pref_nums[' '] = 3

	def time_pref(self, day, time):
		# Takes a day in the format [M|T|W|Th|F] and a military hour btw 8 (8 am) and 23 (11:00pm)
		# returns the preference of this person towards working at that time
		# Return value is a decimal in [0, 0.5, 1, 1.5]
		assert (day.strip(),time) in self.sched_nums, "time_pref: Invalid Day or Time: "+day+" "+str(time)
		return self.sched_nums[(day.strip(),time)]

	def shift_type_pref(self, shift_type, shift_cat):
		# Takes the name of a type of shift as a string.
		# returns a number [1-5] representing this person relative preference to this shift
		# defauts to 3 if there is no preference data for this type/cat

		# give type precedence over category:
		if shift_type in self.pref_nums:
			return self.pref_nums[shift_type]
		elif shift_cat in self.pref_nums:
			return self.pref_nums[shift_cat]
		else:
			return 3

	def shift_pref(self, workshift):
		# Given a workshift object determines this person's relative preference towards it.
		# return value is a number in [0, 7.5] ie [1*0, 5*1.5]

		# compute the time pref of all possible times that this workshift could be done, and take the maximum
		tp = 0
		for start_hr in range(workshift.time, workshift.end_time):
			# time preference starting at start_hr will be the minimum of the time slots that the shift takes up
			# ie the preference rating is the preference of the least desirable hour during the shift
			if start_hr + workshift.hours <= workshift.end_time:
				try:
					t = min([self.time_pref(workshift.day, hr) for hr in range(start_hr, start_hr + int(ceil(workshift.hours))) if start_hr + workshift.hours < 24])

					# ensure there are no conflicting shifts during this time frame
					for shift in self.shifts:
						if shift != workshift and shift.day == workshift.day:
							for shift_time in range(shift.time, shift.time + int(ceil(shift.hours))):
								for ws_time in range(start_hr, start_hr + int(ceil(workshift.hours))):
									if ws_time == shift_time:
										t = 0
					if t > tp:
						tp = t

				except ValueError:
					pass
			
		wp = self.shift_type_pref(workshift.type, workshift.cat) # type pref
		return tp * wp                                           # shift preference = (time pref)*(type pref)

	def available(self, day, time):
		if self.time_pref(day, time) == 0:
			return False
		for shift in self.shifts:
			if shift.day == day and time >= shift.time and time < shift.time+shift.hours:
				return False
		return True

	def rank_shifts(self, shifts):
		# Takes a list of Shift objects and ranks them base on shift_pref
		# saves the list to self.pref_list
		self.pref_list = list(shifts)                                  # make a fresh copy of the list
		self.pref_list.sort(key=lambda shift: self.shift_pref(shift))  # sort by shift_pref

	def combo_pref(self, combo):
		# finds the average rating of shifts in combo
		score = sum([self.shift_pref(shift) for shift in combo])
		return score / len(combo)

	def find_combos(self):
		# finds all different sets of specific time combinations and their average preference
		# this will be used for trading
		self.combos = {}
		def combos(shifts,num,res):
			if num == 0:
				combs.append(res)	
			elif len(shifts) == 0:
				return
			else:
				res.append(shifts[0])
				combos(shifts[1:],num-shifts[0].hours,list(res))
				combos(shifts[1:],num,res[:-1]) 
		for hours in range(25,525,25):
			combs = []
			combos(self.shifts, hours/100., [])
			self.combos[hours/100.] = combs

	def add_shift(self, shift):
		# add shift to curently assigned workshifts
		self.shifts.append(shift)
		self.assigned_hours += shift.hours
		unassigned.remove(shift)

	def rm_shift(self, shift):
		# remove shifts from currently assigned workshifts
		self.shifts.remove(shift)
		self.assigned_hours -= shift.hours
		unassigned.append(shift)

	def add_combo(self, combo, hours):
		for shift in combo:
			self.add_shift(shift)
		self.combos[hours].append(combo)

	def rm_combo(self, combo, hours):
		for shift in combo:
			self.rm_shift(shift)
		self.combos[hours].remove(combo)

class Shift(object):

	blank = None

	def __init__(self, type, day, time,etime, hours, cat):
		self.type = type                                         # kind of workshift; should be in shift_types
		self.day = day                                           # day of the week ie [M|T|W|Th|F|S|Su]
		self.time = time                                         # military start time of the start of the workshift; should be between 8 (am) and 23 (11:00pm)
		self.end_time = etime                                  # end time of workshift 
		assert self.time >= 8 and self.time <= 23, "Shift: Invalid Time: " + str(self.time)
		self.hours = hours                                       # Length of the shift in hours   
		self.cat = cat                                           # Category: ie Dishroom, etc.

	def __eq__(self, other):
		# overrides default == behavior.  Shifts are equal iff:
		# 	- are of the same type
		# 	- occur on the same day
		#	- are at the same time
		if other == None:
			return False
		return self.day == other.day and self.time == other.time and self.type == other.type

	def __str__(self):
		# so that shift objects are printed in a human readable way for debugging purposes
		return "{0}:{1}:{2}".format(self.type, self.day, self.time)

	def __repr__(self):
		# so that lists of shift objects are printed using __str__
		return str(self)

	@staticmethod
	def load(file_):
		# loads a list of shifts from a file
		f = open(file_)
		shifts = []                          # return value
		for line in f.readlines():           # Each line represents a workshift
			if line != "":
				line = line.strip()              # remove pesky newline
				sect = line.split(",")
				type_ = sect[0]
				days = sect[1].split("|")        # Create a seperate shift for each day
				time = 8 if "*" in sect[2] else int(sect[2])
				etime = 24 if "*" in sect[3] else int(sect[3])
				hrs = float(sect[4])
				people_needed = int(sect[5])      # Create a seperate shift for each person needed
				cat = sect[6]
				for day in days:
					for _ in range(people_needed):
						shifts.append(Shift(type_, day, time, etime, hrs, cat))
		Shift.blank = Shift("Vacuum", "T",22,23, 0,"Vaccuum")
		return shifts

# LOAD DATA #

# load the people
people = Person.load(data_path + os.sep + "people.txt")
assert len(people) > 0, "No People Loaded: empty people.txt file?"

#load the shifts
shifts = Shift.load(data_path + os.sep + "shifts.csv")

# check to make sure we have enough workshifts
shift_hours = sum([s.hours for s in shifts]) 
people_hours = sum([p.hours for p in people])
assert shift_hours >= people_hours, "Not enough workshifts: have {0} but need {1}".format(shift_hours, people_hours)

# MAIN #

# Create a ranked list of preferences for each person
for person in people:
	person.rank_shifts(shifts)

unassigned = list(shifts)
active = list(people)

# STAGE 1 #
# Create a valid matching

count = 0
while active and count < timeout:
	victim = random.choice(people)
	if victim.shifts:
		victim.rm_shift(victim.shifts[-1])
	while active:
		random.shuffle(active)
		for person in active:                                                                           # while there exists a person with less than 5/3 hours
			if person.hours <= person.assigned_hours:                      								# if person already has more or equal to the hoursd they need to be assigned
				active.remove(person)                                                                   # remove from active list
				continue
			else:
				if person.pref_list:
					pref = person.pref_list.pop()
					while ((pref == person.locked or pref not in unassigned
							or pref in person.shifts or not person.available(pref.day,pref.time)) 
					 		and person.pref_list):       												# go down pref list until available shift arises
						pref = person.pref_list.pop()													# grab next shift in pref list
					if (person.pref_list):
						person.add_shift(pref)                                                        
				else:
					person.rank_shifts(shifts)                                                          # reset person pref list
					active.remove(person)                                                               # currently not enough shifts in unassigned pool.                                                               

	num = 1                                                                                             # counts the number of people who removed a shift this iteration
	while num != 0:                                                                                     # while someone removed a shift last iteration
		num = 0
		for p in people:
			if p.assigned_hours > p.hours:                                                              # if person is assigned too many hours
				min_hours = min(p.shifts[::-1], key=lambda x: x.hours)                                  # find the lowest preference shift with the least numbr of hours.
				p.rm_shift(min_hours)                                                                   # remove that shift
				p.locked = min_hours                                                                    # prevent it from being chosen next round
				num+=1                                                                                  # record that one person removed a shift this iteration

	active = [person for person in people if person.hours != person.assigned_hours and person.pref_list]   # update active to be only those with incorrect number of hours
	count+=1

for person in people:
		person.find_combos()

print "STAGE 1 COMPLETE"
print "Assignment Time Errors:", check_hours(people)
print "Scheduling Errors:", check_zeros(people)
print "Average Optimality:", avg_optimality(people)
print "--------------------------------------------------"

# STAGE 2 #
# Search for a local maximum by trading shifts
# Look for every possible pair of workshifts (a,b) currently owned by (A,B) where:
#	- A and B are different people
#	- a and b are the same length
# 	- The sum of the A.pref(B) and B.pref(A) is greater than B.pref(B) and A.pref(A) (it will increase the average optimality)
#	- A and B are not already doing shift b,a respectively
# if (a,b) meet the requirements, trade

#for personA in people:
#	for personB in people:
#		if personA is not personB:
#			for jobA in personA.shifts:
#				for jobB in personB.shifts:
#					if jobA.hours == jobB.hours:
#					    if personB.shift_pref(jobA) + personA.shift_pref(jobB) > personA.shift_pref(jobA) + personB.shift_pref(jobB):
#							if (jobB not in personA.shifts and jobA not in personB.shifts):
#								if personA.available(jobB.day,jobB.time) and personB.available(jobA.day, jobA.time):
#									swap(personA.shifts, jobA, personB.shifts, jobB)

for personA in people:
	for personB in people:
		if personA is not personB:
			for hours in range(25,525,25):
				for combA in personA.combos[hours/100.]:
					for combB in personB.combos[hours/100.]:
						if personB.combo_pref(combA) + personA.combo_pref(combB) > personA.combo_pref(combA) + personB.combo_pref(combB):
							if combA in personA.combos[hours/100.] and combB in personB.combos[hours/100.]:
								personA.rm_combo(combA, hours/100.)
								personB.add_combo(combA, hours/100.)
								personB.rm_combo(combB, hours/100.)
								personA.add_combo(combB, hours/100.)
								personA.find_combos()
								personB.find_combos()
								
print "STAGE 2 COMPLETE"
print "Assignment Time Errors:", check_hours(people)
print "Scheduling Errors:", check_zeros(people)
print "Average Optimality:", avg_optimality(people)
print "--------------------------------------------------"

# Stage 3 #
# Trade for shifts still in the unassigned pool
# foreach shift in every person, look through all the shifts in unassigned and see if there's 
# anything that is better.  If so, swap it out.

for person in people:
	for shift in person.shifts:
		for other in unassigned:
			if other.hours == shift.hours and person.shift_pref(other) > person.shift_pref(shift):
				if other not in person.shifts:
					if person.available(other.day,other.time):
						if other in unassigned and shift in person.shifts:
							swap(person.shifts, shift, unassigned, other)

print "STAGE 3 COMPLETE"
print "Assignment Time Errors:", check_hours(people)
print "Scheduling Errors:", check_zeros(people)
print "Average Optimality:", avg_optimality(people)
print "--------------------------------------------------"

# Stage 4 #
# Fix all scheduling errors

for num, personA in enumerate(people):
	for shiftA in personA.shifts:
		while personA.shift_pref(shiftA) == 0 and personA.pref_list:
			rankings = {personB:personB.shift_pref(shiftA) for personB in people}
			rank = rankings.keys()
			rank.sort(key=lambda x: rankings[x])
			while rank:
				personB = rank.pop()
				if personB.shift_pref(shiftA) > 0:
					for jobB in personB.shifts[::-1]:
						if jobB.hours == shiftA.hours and personA.shift_pref(jobB) > 0:
							swap(personA, shiftA, personB, jobB)
							rank = None
			while personA.pref_list:
				next_choice = personA.pref_list.pop()
				if next_choice.hours == personA.hours:
					shiftA = next_choice

print "STAGE 4 complete"
print "People with shift schedule conflicts:", check_zeros(people)
print "People with incorrect number of hours:", check_hours(people)
print "Optimality: ", avg_optimality(people)

# Print Error Report

if check_zeros(people) > 0 or check_hours(people) > 0:
	print "--------------------------------------------------"
	print "ERRORS:"
	for p in people:
		for ws in p.shifts:
			if p.shift_pref(ws) == 0:
				print "Scheduling Error: {0} {1} {2}".format(p.name, ws.type, ws.time)

# Write master log (for debugging purposes)

f = open(data_path + os.sep + "log.html","w")
shift_types = {w.type for w in shifts}
f.write("<h1>Master Log</h1>")
f.write("<table border=1><tr><td>Shift</td><td>Monday</td><td>Tuesday</td><td>Wednesday</td><td>Thursday</td><td>Friday</td><td>Saturday</td><td>Sunday</tr>")
for w in shift_types:
	f.write("<tr><td>"+w+"</td>")
	assigned = ["<td>"]*7
	for person in people:
		for shift in person.shifts:
			if shift.type == w:
				assigned[day_desc.index(shift.day.strip())] += person.name + " " + str(convert_time(shift.time) + " ({0})".format(person.shift_pref(shift))) + "<br/>"
	assigned = [a+"</td>" for a in assigned]
	f.write("".join(assigned) + "</tr>")
f.write("</table>")
for person in people:
	f.write("<h2>{0} ({1})</h2><br/>".format(person.name, sum([w.hours for w in person.shifts])))
	f.write("<table width=100% border=1><tr>"+"".join(["<td>{0}</td>".format(i) for i in range(8,24)])+"</tr>")
	for day in day_desc:
		f.write("<tr>")
		for hour in range(8,24):
			f.write("<td>{0}<br/>".format(person.time_pref(day,hour)))
			for w in person.shifts:
				if w.time <= hour and hour < w.time+w.hours and w.day.strip() == day:
					f.write("<font color=#FF0000 >" if person.shift_pref(w) == 0 else "<font>")
					f.write(str(w)+"</font><br/>")
			f.write("</td>")
		f.write("</tr>")
	f.write("</table>")
f.close()

# Write matching to file in csv format
# Format:
# 	Shift name, Monday, Tuesday, ..., Sunday
# 	Monday, ... Sunday contain the workshifters assigned on that day and the time of the assignment 
#   Note that times are in 24 hour time format
# Example:
# 	Radicalius, Pots, Th, 19, Bathroom Clean, Tu, 9

f = open(data_path + os.sep + "res.csv", "w")
shift_types = {w.type for w in shifts}
f.write("Shift\tMonday\tTuesday\tWednesday\tThursday\tFriday\tSaturday\tSunday\n")
for w in shift_types:
	f.write(w+"\t")
	assigned = ["'"]*7
	for person in people:
		for shift in person.shifts:
			if shift.type == w:
				assigned[day_desc.index(shift.day.strip())] += person.name + " " + str(convert_time(shift.time)) + "\n"
	assigned = [a+"'" for a in assigned]
	f.write("\t".join(assigned) + "\n")
f.close()
