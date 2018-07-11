#!/usr/bin/python
import csv, sys, argparse

def processGeoSubjects(entries):
	geo_indexes = []
	geo_subjects = []
	new_geo = set()
	geo_matched = False
	#pull subject translations from csv file
	with open("geo.csv", 'rt') as g:
		reader = csv.reader(g, dialect='excel', encoding='utf-8')
		for row in reader:
			geo_subjects.append(row)
	#get the indexes of the geo subject columns
	for i, col in enumerate(entries[0]):
		if col == "Subject:geographic":
			geo_indexes.append(i)
	#go through each row and reconcile the values in each geo column against geo_subjects list
	#add values not found to new_geo list
	for row in entries:
		for i in geo_indexes:
			if row[i].strip() != "":
				for geo in geo_subjects:
					if row[i].strip() == geo[0]:
						geo_matched = True
						break
				if geo_matched == False:
					new_geo.add(row[i].strip())
				else:
					geo_matched = False
	# add new subjects to the geo subject list for output and manual checking
	for new in new_geo:
		geo_subjects.append([new, ''])
	with open("geo_updated.csv", 'wb') as ng:
		writer = csv.writer(ng, dialect='excel')
		for row in geo_subjects:
			writer.writerow(row)


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
	argsparser.add_argument('csv', help='csv filename')
	args = argsparser.parse_args()
	inputfile = args.csv

	#import container data from csv file, csv should be encoded UTF-8
	with open(inputfile, 'rt') as f:
		reader = csv.reader(f, dialect='excel', encoding='utf-8')
		for row in reader:
			entries.append(row)
	cleanFields(entries)
	processGeoSubjects(entries)

if __name__ == "__main__":
   main()
