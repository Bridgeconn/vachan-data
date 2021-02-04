import os
import gc
import re
import string
import traceback
import Levenshtein
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer


class PostChecker:

	def __init__(self):
		self.corpora_path = ''


	def clean_text(self, text):
		text = re.sub('[“”]', '"', text)
		text = re.sub('।', '', text)
		text = text.translate(str.maketrans('', '', string.punctuation))
		text = re.sub('\s\s+', ' ', text)
		return text.lower().strip()
	

	def find_cosine_similarity(self, string1, string2):
		try:
			string1 = self.clean_text(string1)
			string2 = self.clean_text(string2)
			vectorizer = CountVectorizer().fit_transform([string1, string2])
			vectors = vectorizer.toarray()
			vec1 = vectors[0].reshape(1, -1)
			vec2 = vectors[1].reshape(1, -1)
			# print(string1, " / ", string2)
			return cosine_similarity(vec1, vec2)[0][0]
		except Exception as e:
			print(e)  
			traceback.print_exc() 


	def main(self):
		try:
			print("\n..................... Post checking the alignments ......................\n")
			self.corpora_path = str(Path(os.getcwd()).parent) + '/corpora/'
			for book in sorted(os.listdir(self.corpora_path)):
				print("\n************************ Book : ",book, '****************************\n')
				for min_lang in os.listdir(self.corpora_path + book):
					print("\n\nmin_lang :: ",min_lang)
					lang_name = min_lang.split('_')[0]
					source_file = book + '_hindi.txt'
					target_file = book + '_' + lang_name + '.txt'
					post_file = book + '_' + lang_name + '_checked.txt'
					source_lines = open(self.corpora_path + book + '/' + min_lang + '/' + source_file, 'r').readlines()
					target_lines = open(self.corpora_path + book + '/' + min_lang + '/' + target_file, 'r').readlines()
					if len(source_lines) != len(target_lines):
						# print("Mismatch in number of lines.........")
						break
					data = ''	
					for index,s_line in enumerate(source_lines):
						s_line = s_line.split('\t')[-1]
						t_line = (target_lines[index]).split('\t')[-1]
						words_diff  = abs(len(s_line.split()) - len(t_line.split()))
						if words_diff > 15:
							# print("----------------------------------------------------------------------------------------")
							edit_ratio = Levenshtein.ratio(s_line,t_line)
							cosine_score = self.find_cosine_similarity(s_line,t_line)
							# print("\n\nwords_diff: ",words_diff, ' , edit_ratio: ',edit_ratio, 'cosine : ', cosine_score)
							# print("....", source_lines[index])
							# print(">>>>", target_lines[index])
							if cosine_score < 0.1 and edit_ratio < 0.35:
								# print("status :  wrong alignment")
								data += (target_lines[index]).strip() + '\t' + 'WRONG ALIGNMENT' + '\n'
							else:
								data += target_lines[index] 	
						else:
							data += target_lines[index]		
					fp = open(self.corpora_path + book + '/' + min_lang + '/' + post_file, 'w')	
					fp.write(data)
					fp.close()
				
		except Exception as e:
			print(e)
			traceback.print_exc()


obj = PostChecker()
obj.main()
