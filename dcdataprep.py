#!/usr/bin/python
import csv, sys, argparse

reload(sys)  
sys.setdefaultencoding('utf8')

def dateIsYear(date):
	if len(date) == 4:
		try: 
			int(date)
			return True
		except ValueError:
			return False
	else:
		return False

def processQuestionableDate(date):
	if len(date) == 5 and date[4] == "?":
		if dateIsYear(date[:4]):
			return [date[:4]+"-01-01", date[:4]+"-12-31"]
		elif date[2:4] == "--": #eg: date is 19--
			return [date[:2]+"00-01-01", date[:2]+"09-12-31"]
		elif date[3:4] == "-": #eg date is 192-
			return [date[:3]+"0-01-01", date[:3]+"9-12-31"]
		else:
			return ["", ""]
	else:
		return ["", ""]
		
		
def processBetweenDate(date):
	dates = ["", ""]
	if date.startswith("between "): #hack it off  and only continue processing if it was present in the first place
		date = date[8:]
		if date.endswith("?"): #hack that off as well
			date = date[:-1]
		if " and " in date: #split the string on that
			dates = date.split(" and ")
		if dateIsYear(dates[0].strip()) and dateIsYear(dates[1].strip()):
			dates[0] = dates[0].strip()+"-01-01"
			dates[1] = dates[1].strip()+"-12-31"
	return dates
		
def stripDateBrackets(date):
	if date.startswith('[') and date.endswith(']'):
		return date[1:-1]
	else:
		return date	
		
def standarizeCirca(date):
	if date.startswith("c") or date.startswith("ca") or date.startswith("circa"):
		try:
			return "circa " + "".join(date[date.index(" ")+1:].split())
		except ValueError: #likely there is no space between c or ca. before date
			if date.startswith("ca.") and not date.startswith("ca. "):
				return "circa " + "".join(date[3:].split())
			elif date.startswith("c") and not date.startswith("c "):
				return "circa " + "".join(date[1:].split())
			else:
				return date
	else:
		return date
		
def processCircaDate(date):
	dates = ["",""]
	if date.startswith("circa "):
		date = date[6:].strip()
		print date
	if "?" in date:
		print date
		dates = processQuestionableDate(date)
	elif dateIsYear(date):
		dates[0] = date + "-01-01"
		dates[1] = date + "-12-31"
	return dates
		
	
def processDates(entries):
	cr_date = ""
	try:
		#get the index of the Date:creation field and set insert points for begin and end dates
		cr_date_ind = entries[0].index("Date:creation")
		begin_date_ind = cr_date_ind + 1
		end_date_ind = cr_date_ind + 2
		for row in entries:
			print row[0]
			dates = ["", ""]
			#add header values for Begin date and End date
			if "Date:creation" in row:
				row.insert(begin_date_ind, "Begin date")
				row.insert(end_date_ind, "End date")
				
			else:
				cr_date = row[cr_date_ind].strip()
				cr_date = stripDateBrackets(cr_date)
				cr_date = standarizeCirca(cr_date)
				if len(cr_date) < 7:
					cr_date = "".join(cr_date.split()) #get rid of extraneous whitespace on questionable dates like 192 -? or 192- ?
				row[cr_date_ind] = cr_date
				if dateIsYear(cr_date):
					dates[0] = cr_date + "-01-01"
					dates[1] = cr_date + "-12-31"
				elif "?" in cr_date and "between" not in cr_date and "circa" not in cr_date:
					dates = processQuestionableDate(cr_date)
				elif cr_date.startswith("between"):
					dates = processBetweenDate(cr_date)
				elif cr_date.startswith("circa"):
					dates = processCircaDate(cr_date)
				row.insert(begin_date_ind, dates[0])
				row.insert(end_date_ind, dates[1])
		

	except:
		print "Unexpected error:", sys.exc_info()[0]
		raise
	
def processGeoSubjects(entries):
	geo_indexes = []
	geo_subjects = []
	#pull subject translations from csv file
	with open("geo.csv", 'rt') as g:
		reader = csv.reader(g, dialect='excel')
		for row in reader:
			geo_subjects.append(row)
	#get the indexes of the geo subject columns
	for i, col in enumerate(entries[0]):
		if col == "Subject:geographic":
			geo_indexes.append(i)
	#go through each row and reconcile the values in each geo column against geo_subjects list
	for row in entries:
		for i in geo_indexes:
			if row[i] != "":
				for geo in geo_subjects:
					if row[i] == geo[0]:
						row[i] = geo[1]
						
def addLocalIdentifier(entries, identifier):
	insertIndex = entries[0].index("Identifier:roger record") + 1
	for row in entries:
		if "Identifier:roger record" in row:
			row.insert(insertIndex, "Identifier:local")
		else:
			row.insert(insertIndex, identifier)
			
#add code to clean straggling punctuation at beginning/end of field entries
def cleanFields(entries): 
	for row in entries:
		for entry in row:
			entry = entry.strip()
			if entry.startswith(',') or entry.startswith(';') or entry.startswith(':') or entry.startswith('.'):
				entry = entry[1:]
			if entry.endswith(',') or entry.endswith(';') or entry.endswith(':'):
				entry = entry[0:-1]
		
			
def main():
	entries = []
	inputfile = ''
	outputfile = ''
	argsparser = argparse.ArgumentParser()
	argsparser.add_argument('csv', help='csv filename (without the .csv extension)')
	args = argsparser.parse_args()
			
	inputfile = args.csv + '.csv'
	outputfile = args.csv + '_processed.csv'
	
	#import container data from csv file, csv should be encoded UTF-8
	with open(inputfile, 'rt') as f:
		reader = csv.reader(f, dialect='excel')
		for row in reader:
			entries.append(row)
	cleanFields(entries)
	processDates(entries)
	addLocalIdentifier(entries, "scarare")
	processGeoSubjects(entries)
	with open(outputfile, 'wb') as w:
		writer = csv.writer(w)
		writer.writerows(entries)
	
if __name__ == "__main__":
   main()
