import re
 
def timestamp(doc):
	regex = re.compile(r'\d*:\d\d')
	matchobj = regex.search(doc)
	if(matchobj == None):
		return False
	return True

def senti(doc,sentidict):
	senti3 = 0
	senti6 = [0,0,0,0,0,0]
	for senti in sentidict:
		if senti.word in doc:
			senti3 += int(senti.class3)
			senti6[int(senti.class6)] += 1
	return [senti3, senti6.index(max(senti6))]