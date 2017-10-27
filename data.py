# Dataset Generation and Testing Functions

import random,os,sys

# CONSTANTS #

syms = [' ','-','+','x']
day_desc = ["M","T","W","Th","F","S","Su"]
data_path = "data"

# load types of shifts from file
f = open(data_path + os.sep + "types.txt")
cont = f.readlines()
shift_types = [i.strip() for i in cont]

# FUNCTIONS #

def random_people(num):
	# takes a number num and generates the contents of a valid people.txt file containing num people

	result = ""                   # stores return value

	for _ in range(num):
		entry = ""
		entry += str(_)+"\n"      # name will just be number
		entry += str(random.choice([3,5]))+"\n"            # Everyone has 5 hours of workshift ( for now )
		for i in range(7):
			day = ""
			for j in range(16):
				day += random.choice(syms)  # each sym represents an hour of the day.
			entry+=day+"\n"
		for k in range(len(shift_types)):
			entry+=str(random.randint(1,5))
		entry+="\n[END]\n"
		result+=entry
	return result

def save_people(num):
	f = open(data_path + os.sep + "people.txt","w")
	f.write(random_people(num))
	f.close()

def random_shifts(num):
	result = ""
	for _ in range(num):
		entry = ""
		entry += random.choice(shift_types)+","
		entry += "|".join(list({random.choice(day_desc) for _ in range(random.randint(1, 7))}))+","
		entry += str(random.randint(8,23))+","
		entry += str(random.choice([1,2]))+","
		entry += str(random.randint(1,3))
		result += entry+"\n"
	return result 

def save_shifts(num):
	f = open(data_path + os.sep + "shifts.csv","w")
	f.write(random_shifts(num))
	f.close()

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
		if p.assigned_hours != p.hours:
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

def avg_ranking(people, shifts):
	sum_= 0
	for i in people:
		sum_ += len(shifts) - len(i.pref_list)
	return float(sum_) / len(people)  

def check_dup(people):
	# checks to make sure that no two people are assigned the same shift
	seen = set()
	dups = 0
	for person in people:
		for shift in person.shifts:
			if shift in seen:
				dups+=1
			else:
				seen.add(shift)
	return dups

if __name__ == "__main__":
	people = int(sys.argv[1])
	shifts = int(sys.argv[2])
	save_people(people)
	save_shifts(shifts)
