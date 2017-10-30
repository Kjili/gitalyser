import argparse

keywords = ["S.", "Seite"]
parser = argparse.ArgumentParser(description="Progress tracker based on git commit messages. It analyses all git log messages from a given file that contain a keyword followed by a number (with a space in between). The default use case is to track writing progress in pages with the number representing the current page at the time of the commit (example: " + str(keywords[0]) + " 19). Currently used keywords: " + str(keywords), formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("filename", type=str, help="name of the file to be analysed")
parser.add_argument("-l", dest="log", action="store_true", help="list all commits and exit, this is similar to \"git log --oneline\" of the given file")
parser.add_argument("-m", dest="missing", action="store_true", help="list missing commit messages and exit, messages can be missing (i.e. non-detected) because of missing or wrong keywords or wrong structure in commit messages")
parser.add_argument("-c", default="0000000", metavar="COMMIT HASH", help="the commit in history to compare the latest one with, default is the earliest commit")
parser.add_argument("-t", type=int, default="25", metavar="POS NUMBER", help="the threshold that marks a remarkable change for verbose/recent mode")
parser.add_argument("-n", type=int, default="3", metavar="POS NUMBER", help="the number of latest commits you want to analyse in more detail and the number of commits that are ignored when searching for a recent remarkable change")
parser.add_argument("-r", dest="recent", action="store_true", help="list most recent changes made since the last remarkable backward change which is assumed to be a new iteration of work")
parser.add_argument("-v", dest="verbose", action="store_true", help="list and visualise significant changes")
# TODO add tags (e.g. for recent)
# TODO allow multiple word keywords
# TODO median, mode (np)
# TODO remarkable date, page change
# TODO parse date differently and plot it
# TODO average plot
# TODO add empty list checks
args = parser.parse_args()

import subprocess
import time
import dateutil.parser

filename=args.filename

# list all commits and exit
if args.log:
	subprocess.run(["git", "log", "--oneline", filename])
	quit()

# (pre)process helper functions #

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

# get the commit index for the analysis (if not given by the user this is the first commit in history)
commitIndex = args.c
def getCommitIndex():
	# make sure to only compare against entry[0] which is the hash (in case a hash is given in a message)
	for entry in loglistDetected:
		if commitIndex == entry[0]:
			return loglistDetected.index(entry)
	print("Warning: The given commit hash was not part of a detected git log entry, using default.")
	return len(loglistDetected)-1


# preprocess #

# read hashes and commit messages from log
log = subprocess.run(["git", "log", "--oneline", filename], stdout=subprocess.PIPE).stdout.decode("utf-8")
loglist = log.split("\n")

# parse the loglist
loglistDetected=[]
loglistFailed=[]
for entry in loglist:
	if len(entry) == 0: continue
	# split at first space to split hashes from messages
	entrylist = entry.split(" ", 1)
	
	# read the commit date from the log based on the parsed hash and add it to the entry
	date = subprocess.run(["git", "log", "-1", "--pretty=tformat:%aI", entrylist[0]], stdout=subprocess.PIPE).stdout.decode("utf-8")
	entrylist.append(date.split("\n")[0])
	
	# if a keyword is found in the message check if a number follows
	if any(True for key in keywords if key in entrylist[1]):
		messagelist = entrylist[1].split()
		#keywordIndex = messagelist.index(next(key for key in keywords if key in messagelist))
		found = False
		for messagepart in messagelist:
			if found and messagepart.isdigit():
				entrylist.append(int(messagepart))
				loglistDetected.append(entrylist)	# only analyse those that have a number of pages
				break								# stop if a number is found
			if found:
				loglistFailed.append(entrylist)		# put those that don't in fail
				break								# stop if the structure is unclear to prevent false positives
			if any(True for key in keywords if key in messagepart):
				found = True
				continue
	# if no known keyword is found in the message add it to the failed entries
	else:
		loglistFailed.append(entrylist)

# pretty-print the fail list
if args.missing or len(loglistDetected) == 0:
	for entry in loglistFailed:
		if len(entry) == 3:
			print(entry[0] + "\t" + entry[2] + "\t" + entry[1])
	print(str(len(loglistFailed)) + " entries are not detected.")
	if len(loglistDetected) == 0:
		print("Warning: Keyword detection failed on all entries!")
	quit()

# get lists for the difference in time and pages for two concurrent detected entries each
daydifflist = []
pagedifflist = []
for i in range(len(loglistDetected)-1):
	daydifflist.append(timediff(loglistDetected[i][2], loglistDetected[i+1][2]))
	pagedifflist.append(loglistDetected[i][3] - loglistDetected[i+1][3])


# print helper functions #

def printChange(entry1, entry2):
	days = timediff(entry1[2], entry2[2]) + 1 	# +1 to avoid division by 0
	pages = entry1[3] - entry2[3]
	print("Between: ")
	print(entry1)
	print(entry2)
	print(str(days) + " days total passed while writing " + str(pages) + " pages")
	print("That is an average of " + str(pages/days) + " pages per day")

def printCurrentChange(loglist, numCommits = 3):
	if len(loglist) > numCommits:
		entry1 = loglist[0]
		entry2 = loglist[numCommits-1]
		days = timediff(entry1[2], entry2[2]) + 1 # +1 to avoid division by 0
		pages = entry1[3] - entry2[3]
		average = pages/days
		
		print("For the last " + str(numCommits) + " commits: ")
		for i in range(0, numCommits):
			print(loglist[i])
		print(str(days) + " days total passed while writing " + str(pages) + " pages")
		print("That is an average of " + str(average) + " pages per day")
		print(" - great, keep going! :D" if average >= 2 else " - just a little bit more! :)" if average >= 1.5 else " - don't worry, just do it!")


# process #

threshold = args.t
numCommits = args.n
index1 = 0
index2 = getCommitIndex() if not commitIndex == "0000000" else len(loglistDetected)-1
recentIndex = -1
splitlist = loglistDetected[index1:index2+1] # in the default case this is the whole list

# print analysis
for i in range(len(daydifflist)-1):
	# print remarkable changes
	if args.verbose:
		if (daydifflist[i] > 14):
			print("A long break (more than two weeks) was between: ")
			print(splitlist[i])
			print(splitlist[i+1])
		if (pagedifflist[i] > threshold or pagedifflist[i] < -threshold):
			print("A remarkable change in page difference happened between: ")
			print(splitlist[i])
			print(splitlist[i+1])
	# get recent index
	if args.recent and recentIndex == -1 and i > numCommits and pagedifflist[i] < -threshold:
		#print("Warning: The last commit already marks a remarkable backward change, recent commits will be shown until the next remarkable change in history.")
		recentIndex = i

# overall average
if args.verbose or index2 < len(loglistDetected)-1:
	printChange(loglistDetected[index1], loglistDetected[index2])

# recent average
if args.recent:
	printChange(loglistDetected[index1], loglistDetected[recentIndex])

# current average over a given number of commits (default: 3)
printCurrentChange(loglistDetected, numCommits)


# plotting helper functions

def plotAnalysis(daydifflist, pagedifflist):
	daydifflistAccumulated = []
	daysSum = 0
	for entry in daydifflist[::-1]:
		daysSum += entry
		daydifflistAccumulated.append(daysSum)

	pagedifflistAccumulated = []
	pagesSum = 0
	for entry in pagedifflist[::-1]:
		pagesSum += entry
		pagedifflistAccumulated.append(pagesSum)

	fig0 = plt.figure()
	plt.plot(range(len(daydifflist)), pagedifflist[:])
	plt.title("Writing Curve")
	plt.xlabel("n-th commit in history")
	plt.ylabel("Pages")

	fig1 = plt.figure()
	plt.plot(daydifflistAccumulated[:], pagedifflistAccumulated[:])
	plt.title("Writing Curve")
	plt.xlabel("Day Number")
	plt.ylabel("Page Number")


# plot #

import matplotlib.pyplot as plt
#export NO_AT_BRIDGE=1 in shell if error annoys
if args.verbose:
	daydifflist = daydifflist[index1:index2]
	daydifflist = daydifflist[index1:index2]
	plotAnalysis(daydifflist, pagedifflist)

if args.recent:
	daydifflist = daydifflist[index1:recentIndex]
	pagedifflist = pagedifflist[index1:recentIndex]
	plotAnalysis(daydifflist, pagedifflist)

plt.show()
