import os
import nltk
import textract
import sys, re

def get_resumes(n):
	all_cvs = list()
	for index, file in enumerate(os.listdir("./resumes")):
		if (file[-3:]) in ['pdf', 'docx']:
			text = textract.process("./resumes/" + file)
			all_cvs.append(str(text))
		else:
			continue
		if index >= 1000:
			break
	# print(all_cvs[n])
	return all_cvs

all_resumes = get_resumes(100)
cleaned_cv = all_resumes[1].replace('\\n', '\n')
regex = re.compile('^x..$')
cleaned_cv = list(filter(lambda x: not regex.search(x), re.findall("[A-Z]{2,}(?![a-z])|[\w]+", cleaned_cv)))

print(cleaned_cv)

