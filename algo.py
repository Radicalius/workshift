import sys, os, random
import data

# CONSTANTS #

# relative path to directory containing person.txt, types.txt, and shifts.txt
data_path = "data"
day_desc = ["M","T","W","Th","F","S","Su"]
pref_mult = {'+':1.5, '-':0.5, ' ':1.0, 'x':0}

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
		self.rejected = []
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
		self.pref = cont[9].strip()

		# parse schedule data
		days = self.sched.split("\n")
		for d,i in zip(day_desc, days):    # d is M|T|W|Th|F|S|Su and i is data for that day
			hour = 8                       # start at 8 am
			for j in i:                    # foreach hour of data
				self.sched_nums[(d,hour)] = pref_mult[j]
				hour+=1

		# parse shift preference data
		for ind,char in enumerate(self.pref):             # each charater references a shift type [1-5]
			p = int(char)
			self.pref_nums[shift_types[ind]] = p

	def time_pref(self, day, time):
		# Takes a day in the format [M|T|W|Th|F] and a military hour btw 8 (8 am) and 23 (11:00pm)
		# returns the preference of this person towards working at that time
		# Return value is a decimal in [0, 0.5, 1, 1.5]
		assert (day,time) in self.sched_nums, "time_pref: Invalid Day or Time: "+day+" "+str(time)
		return self.sched_nums[(day, time)]

	def shift_type_pref(self, shift_type):
		# Takes the name of a type of shift as a string.
		# returns a number [1-5] representing this person relative preference to this shift
		assert shift_type in self.pref_nums, "shift_type_pref: Invalid Workshift Type"
		return self.pref_nums[shift_type]

	def shift_pref(self, workshift):
		# Given a workshift object determines this person's relative preference towards it.
		# return value is a number in [0, 7.5] ie [1*0, 5*1.5]
		tp = self.time_pref(workshift.day, workshift.time)       # time pref
		wp = self.shift_type_pref(workshift.type)                # type pref
		return tp * wp                                           # shift preference = (time pref)*(type pref)

	def rank_shifts(self, shifts):
		# Takes a list of Shift objects and ranks them base on shift_pref
		# saves the list to self.pref_list
		self.pref_list = list(shifts)                                  # make a fresh copy of the list
		self.pref_list.sort(key=lambda shift: self.shift_pref(shift))  # sort by shift_pref

class Shift(object):

	def __init__(self, type, day, time, hours):
		self.type = type                                         # kind of workshift; should be in shift_types
		assert self.type in shift_types, "Shift: Invalid Type"
		self.day = day                                           # day of the week ie [M|T|W|Th|F|S|Su]
		self.time = time                                         # military time of the start of the workshift; should be between 8 (am) and 23 (11:00pm)
		assert self.time >= 8 and self.time <= 23, "Shift: Invalid Time"
		self.hours = hours                                       # Length of the shift in hours   
		self.asigned = False                                     # whether this shift has been assigned
		self.asignee = None                                      # who it was assigned to (or None if not applicable)

	def assign(self,p):
		# Assign this shift to Person p
		self.assigned = True
		self.asignee = p

	def free(self):
		# Unassign shift
		self.assigned = False
		self.asignee = None

	def __eq__(self, other):
		return self.day == other.day and self.time == other.time and self.type == other.type

	@staticmethod
	def load(file_):
		# loads a list of shifts from a file
		f = open(file_)
		shifts = []                          # return value
		for line in f.readlines():           # Each line represents a workshift
			if line != "":
				line = line.strip()              # remove pesky newline
				sect = line.split("\t")
				type_ = sect[0]
				days = sect[1].split("|")        # Create a seperate shift for each day
				time = int(sect[2])
				hrs = float(sect[3])
				people_needed = int(sect[4])      # Create a seperate shift for each person needed
				for day in days:
					for _ in range(people_needed):
						shifts.append(Shift(type_, day, time, hrs))
		return shifts

# LOAD DATA #

# load types of shifts from file
f = open(data_path + os.sep + "types.txt")
cont = f.readlines()
shift_types = [i.strip() for i in cont]

# load the people
people = Person.load(data_path + os.sep + "people.txt")

#load the shifts
shifts = Shift.load(data_path + os.sep + "shifts.txt")

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

def remove_equals(lst, item):
	got_in = False
	for i in lst:
		if i == item:
			lst.remove(i)
			got_in = True
			break
	#assert got_in, "Error: item was not found in list"

def is_in(lst, item):
	for i in lst:
		if i == item:
			return True
	return False

print "Starting STAGE 1 ..."

while len(active) > 0:
	random.shuffle(active)
	for person in active:
		if len(person.pref_list) == 0:
			low = min(person.shifts, key=lambda x: x.hours)
			unassigned.append(low)
			person.shifts.remove(low)
			print person.shifts
			person.assigned_hours -= low.hours
			person.pref_list = person.rejected
			person.rejected = []
		if person.assigned_hours == person.hours or len(person.pref_list) == 0:
			active.remove(person)
			continue
		pref = person.pref_list.pop()
		person.rejected.append(pref)
		while (not pref in unassigned or person.assigned_hours + pref.hours > person.hours or pref in person.shifts) and person.pref_list:
			pref = person.pref_list.pop()
		if pref in unassigned and person.assigned_hours + pref.hours <= person.hours:
			unassigned.remove(pref)
			person.shifts.append(pref)
			person.assigned_hours += pref.hours
	print "\tActive:", len(active)

print "STAGE 1 complete\n"

print "People with shift schedule conflicts:", data.check_zeros(people)
print "People with incorrect number of hours:", data.check_hours(people)
print "Optimality: ", data.avg_optimality(people)

print "\nStarting STAGE 2 ..."

for num, personA in enumerate(people):
	for personB in people:
		if personA is not personB:
			for jobA in personA.shifts:
				for jobB in personB.shifts:
					if jobA.hours == jobB.hours and personB.shift_pref(jobA) + personA.shift_pref(jobB) > personA.shift_pref(jobA) + personB.shift_pref(jobB):
						if (jobB not in personA.shifts and jobA not in personB.shifts):
							remove_equals(personA.shifts, jobA)
							personA.shifts.append(jobB)
							remove_equals(personB.shifts, jobB)
							personB.shifts.append(jobA)
	print "\t{0}/{1} people complete".format(num, len(people))

print "STAGE 2 complete\n"

print "People with shift schedule conflicts:", data.check_zeros(people)
print "People with incorrect number of hours:", data.check_hours(people)
print "Optimality: ", data.avg_optimality(people)

print "\nStarting STAGE 3 ..."

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
							remove_equals(personA.shifts, shiftA)
							personA.shifts.append(jobB)
							remove_equals(personB.shifts, jobB)
							personB.shifts.append(shiftA)
							rank = None
			while personA.pref_list:
				next_choice = personA.pref_list.pop()
				if next_choice.hours == personA.hours:
					shiftA = next_choice
	print "\t{0}/{1} people complete".format(num, len(people))

print "STAGE 3 complete\n"

print "People with shift schedule conflicts:", data.check_zeros(people)
print "People with incorrect number of hours:", data.check_hours(people)
print "Optimality: ", data.avg_optimality(people)
print "Duplicate Check: ", "PASSED" if data.check_dup(people) > 0 else "FAILED"

print
for i in people:
	s = "\t".join(["{0};{1};{2}".format(s.type,s.day,s.time,s.hours) for s in i.shifts])
	print i.name+"\t"+s