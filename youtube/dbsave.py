# coding: utf8
import csv
from .models import WordDict

def dbWordDict():
	cmt_path = "senti_dict.csv"
	with open(cmt_path, 'r', encoding='utf-8') as senti_file:
		reader = csv.reader(senti_file)
		for row in reader:
			word = WordDict(word = row[0], class3 = int(row[1]), class6 = int(row[2]))
			word.save()