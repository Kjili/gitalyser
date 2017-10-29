import subprocess
import time
import dateutil.parser
import argparse

parser = argparse.ArgumentParser(description="Progress Tracker based on git commit messages. \nKeywords are \"S.\" and \"Seite\" followed by a number.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("filename", type=str, help="name of the file to be analysed")
parser.add_argument("-l", dest="log", action="store_true", help="list all possible commits")
parser.add_argument("-m", dest="missing", action="store_true", help="list missing commit messages and exit (messages can be missing because of missing or wrong keywords or wrong structure in commit messages)")
parser.add_argument("-v", dest="verbose", action="store_true", help="list and visualise significant changes")
parser.add_argument("-c", default="0", metavar="COMMIT HASH", help="the commit in history to compare the latest one with, default is the earliest commit")
parser.add_argument("-r", dest="recent", action="store_true", help="list most recent changes made since the last remarkable change which is assumed to be a new iteration of work")
# TODO median, mode (np)
# TODO remarkable date, page change
# TODO parse date differently and plot it
# TODO average plot
# TODO without verbose, no change in print is seen for stating commit -> change
args = parser.parse_args()

filename=args.filename

if args.log:
	subprocess.run(["git", "log", "--oneline", filename])
	quit()

# read hashes and commit messages from log
messages = subprocess.run(["git", "log", "--oneline", filename], stdout=subprocess.PIPE).stdout.decode("utf-8")
messages = messages.split("\n")

a=[]
for e in messages:
	a.append(e.split(" ", 1))	# split at first space to split hashes from messages

# parse log for correctly parsable entries and failed entries
a_correct=[]
a_fail=[]
for e in a:
	if len(e) < 2: continue
	if "bis S. " in e[1] or "bis Seite " in e[1]:
		# read dates from log based on hashes read before (if a keyword is found in the message)
		date = subprocess.run(["git", "log", "-1", "--pretty=tformat:%aI", e[0]], stdout=subprocess.PIPE).stdout.decode("utf-8")
		e.append(date.split("\n")[0])
		substrings = e[1].split()
		found = False
		for s in substrings:
			if found and s.isdigit():
				e.append(int(s))
				a_correct.append(e)		# only analyse those that have a number of pages
				break					# stop when one number is found
			if found:
				a_fail.append(e)		# put those that don't in fail
				break					# stop if the structure is unclear to prevent false positives
			if "S." in s or "Seite" in s:
				found = True
				continue
	else:
		a_fail.append(e)

# pretty-print the fail list
if args.missing:
	for i in a_fail:
		# uncomment and move date out of "if" above to add a date to every commit if that should prove useful
		#if len(i) >= 3:
		#	print(i[0] + "\t" + i[1] + "\t" + i[2])
		if len(i) == 2:
			print(i[0] + "\t" + i[1])
	quit()

# get the difference in days between two points in time given in iso format
def timediff(isotime1, isotime2):
	#time1 = time.strptime(isotime1, "%Y-%m-%dT%H:%M:%S")	# problems with last piece
	#time2 = time.strptime(isotime2, "%Y-%m-%dT%H:%M:%S")
	#time1 = time.mktime(time1)
	#time2 = time.mktime(time2)
	#return int(time2-time1) / 86400
	d1 = dateutil.parser.parse(isotime1)
	d2 = dateutil.parser.parse(isotime2)
	return (d1-d2).days

threshold = -25 # defines what is seen as recent through remarkable changes in pages that are larger than -50
def analyse(lst, index1, index2, recentIndex = -1):	
	# prepare arrays
	daysArray = []
	pagesArray = []
	splitlist = lst[index1:index2]
	#TODO fix!
	print(len(splitlist))
	print(len(lst))
	
	for j in range(len(splitlist)-1):
		# iterate through the list and get difference in time and pages for two concurrent elements each
		daysArray.append(timediff(splitlist[j][2], splitlist[j+1][2]))
		pagesArray.append(splitlist[j][3] - splitlist[j+1][3])
		
		# print remarkable changes
		if args.verbose:
			if (daysArray[-1] > 14):
				print("A long break (more than two weeks) was between: ")
				print(splitlist[j])
				print(splitlist[j+1])
			if (pagesArray[-1] > 20 or pagesArray[-1] < -20):
				print("A remarkable change in page difference happened between: ")
				print(splitlist[j])
				print(splitlist[j+1])
		
		# if recent is requested
		if args.recent and pagesArray[-1] < threshold and recentIndex == -1:
			recentIndex = j
	
	# overall average
	if args.verbose:
		item1 = lst[index1]
		item2 = lst[index2]
		days = timediff(item1[2], item2[2]) + 1 # +1 to avoid division by 0
		pages = item1[3] - item2[3]
		
		print("For: ")
		print(item1)
		print(item2)
		print(str(days) + " days total passed while writing " + str(pages) + " pages")
		#print("That is an average of " + str(pages/days) + " pages per day")
	
	# recent average
	if args.recent:
		item1 = lst[index1]
		item2 = lst[recentIndex]
		days = timediff(item1[2], item2[2]) + 1 # +1 to avoid division by 0
		pages = item1[3] - item2[3]
		
		print("Between: ")
		print(item1)
		print(item2)
		print(str(days) + " days total passed while writing " + str(pages) + " pages")
		print("That is an average of " + str(pages/days) + " pages per day")
	
	# three-days average
	if len(daysArray) >= 3:
		item1 = lst[0]
		item2 = lst[2]
		days = timediff(item1[2], item2[2]) + 1 # +1 to avoid division by 0
		pages = item1[3] - item2[3]
		average = pages/days
		
		print("For the last three commits: ")
		print(item1)
		print(lst[1])
		print(item2)
		print(str(days) + " days total passed while writing " + str(pages) + " pages")
		print("That is an average of " + str(pages/days) + " pages per day")
		print(" - great, keep going! :D" if average >= 2 else " - just a little bit more! :)" if average >= 1.5 else " - don't worry, just do it!")
	
	return daysArray, pagesArray, recentIndex

# find commit index for analysis (if not given by users this is the first commit in history)
def getCommitIndex():
	commitIndex = len(a_correct) - 1
	for el in a_correct:
		if args.c == el[0]:
			return a_correct.index(el)

# analyse
index1 = 0
index2 = getCommitIndex() if not args.c == "0" else -1
daysArray, pagesArray, recentIndex = analyse(a_correct, index1, index2)

# draw
import matplotlib.pyplot as plt
if args.verbose:
	#export NO_AT_BRIDGE=1 in shell if error annoys
	
	#todo make better
	totalDaysArray = []
	daysSum = 0
	for entry in daysArray[::-1]:
		daysSum += entry
		totalDaysArray.append(daysSum)

	totalPagesArray = []
	pagesSum = 0
	for entry in pagesArray[::-1]:
		pagesSum += entry
		totalPagesArray.append(pagesSum)
	
	fig0 = plt.figure()
	plt.plot(range(len(daysArray)), pagesArray[:])
	plt.title("Writing Curve")
	plt.xlabel("n-th commit in history")
	plt.ylabel("Pages")
	
	fig1 = plt.figure()
	plt.plot(totalDaysArray[:], totalPagesArray[:])
	plt.title("Writing Curve")
	plt.xlabel("Day Number")
	plt.ylabel("Page Number")

if args.recent:
	daysArray = daysArray[index1:recentIndex]
	pagesArray = pagesArray[index1:recentIndex]
	
	#todo make better
	totalDaysArray = []
	daysSum = 0
	for entry in daysArray[::-1]:
		daysSum += entry
		totalDaysArray.append(daysSum)

	totalPagesArray = []
	pagesSum = 0
	for entry in pagesArray[::-1]:
		pagesSum += entry
		totalPagesArray.append(pagesSum)
	
	print(sum(daysArray), totalDaysArray[-1])
	
	fig2 = plt.figure()
	plt.plot(range(len(daysArray)), pagesArray[:])
	plt.title("Writing Curve")
	plt.xlabel("n-th commit in history")
	plt.ylabel("Pages")
	
	fig3 = plt.figure()
	plt.plot(totalDaysArray[:], totalPagesArray[:])
	plt.title("Writing Curve")
	plt.xlabel("Day Number")
	plt.ylabel("Page Number")

plt.show()
