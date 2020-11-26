import gc
import os
import json
import logging
import traceback
import pandas as pd
from datetime import datetime
from collections import defaultdict
from nltk.translate.bleu_score import sentence_bleu

from config import get_db, close_db

if 'logs' not in os.listdir(os.getcwd() + '/'):
	os.mkdir(os.getcwd() + '/logs')
logging.basicConfig(filename='logs/quality_analyzer_logs.log', format='%(asctime)s: %(message)s',
					datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger('logs/quality_analyzer_logs.log')
logger.setLevel(logging.DEBUG)

languages = {'mandeali', 'bhadrawahi'}


class QualityAnalyzer:

	def __init__(self, lang, target_lang, domain):
		self.cwd = ''
		self.lang = lang
		self.target_lang = target_lang
		self.domain = domain


	def tag_data(self, path, file, set_tag):
		data_lines = open(path + file, 'r').readlines()
		filename = file.split('.')[0]
		sgml_file = path + filename+'.sgml'
		fp = open(path + filename+'.sgml', 'w')
		data = '<'+set_tag+' setid="NT" srclang="'+self.lang+'" trglang="'+self.target_lang+'">\n<DOC docid="'+filename+'" sysid="src1">'
		for index, line in enumerate(data_lines):
			data += '\n<seg id="'+str(index+1)+'">'+line+"</seg>"
		data += '\n</DOC></'+set_tag+'>'
		fp.write(data)
		fp.close()
		return sgml_file
			

	def generate_blue(self):
		try:
			data_path = self.cwd + 'data/'
			source_path = data_path + 'source/'+self.lang +'/'
			reference_path = data_path + 'references/'+self.target_lang +'/'
			hyp_path = data_path + 'hypothesis/'+self.target_lang +'/'
			out_path = data_path + 'output/'+self.target_lang +'/'
			if self.target_lang not in os.listdir(data_path + 'output/'):
				os.mkdir(data_path + 'output/' + self.target_lang)
			for file in os.listdir(source_path):
				if not file.endswith('txt'):
					continue
				print("File : ", file)	
				source_file = self.tag_data(source_path, file, 'srcset')
				reference_file = self.tag_data(reference_path, file, 'refset')
				hyp_file = self.tag_data(hyp_path, file, 'tstset')
				# print(source_file, reference_file, hyp_file)
				print('perl mteval-v13.pl $0 -r ' + reference_file + ' -s ' + source_file + ' -t ' + hyp_file)
				os.system('perl mteval-v13.pl $0 -r ' + reference_file + ' -s ' + source_file + ' -t ' + hyp_file + '> '+out_path+file)

		except Exception as e:
			print(e)
			msg = traceback.format_exc()
			logger.info(msg)	

	def check_quality(self):
		logger.info("Checking quality...")
		reference_path = self.cwd + 'references/' + self.lang + '/'
		token_dic = json.load(open(reference_path + 'token_translations.json'))
		df = pd.read_csv('bible_tokens_translation_into_mai.csv')
		for index, row in df.iterrows():
			# print(".....", row['tokens'])
			token = row['tokens'] + '_' + self.target_lang + '_' + self.domain
			if token in token_dic:
				# print("//////////")
				references = [item.split() for item in token_dic[token]]
				# print('reference : ', references)
				# print('hypothesis : ', row['translations'].split())
				score = sentence_bleu(references, row['translations'].split())
				print(score)

	def build_reference_dic(self, connection):
		start = datetime.now()
		logger.info("Building references")
		if 'references' not in os.listdir(self.cwd):
			os.mkdir(self.cwd + 'references')
		reference_path = self.cwd + 'references/'
		cursor = connection.cursor()
		cursor.execute("SELECT m.source_token, m.target_token, sl.language_name as source_lang, tl.language_code as target_lang, s.domain FROM translation_memories as m LEFT JOIN sources as s ON m.source_id = s.source_id LEFT JOIN languages as sl ON m.source_language_id = sl.language_id LEFT JOIN languages as tl ON m.target_language_id = tl.language_id ORDER BY m.source_id;")
		result = cursor.fetchall()
		# print(result)
		for language in languages:
			print(language)
			token_dic = defaultdict(list)
			if language not in os.listdir(reference_path):
				os.mkdir(reference_path + language)
			lang_result = [list(item) for item in result if item[2].lower() == language]
			for item in lang_result:
				if item[1] is None:
					continue
				if item[0] + '_' + item[3] + '_' + item[4] not in token_dic:
					token_dic[item[0] + '_' + item[3] + '_' + item[4]] = [item[1]]
				elif item[1] not in token_dic[item[0] + '_' + item[3] + '_' + item[4]]:
					token_dic[item[0] + '_' + item[3] + '_' + item[4]].append(item[1])
			with open(reference_path + language + '/token_translations.json', 'w') as fp:
				json.dump(token_dic, fp, ensure_ascii=False)
		logger.info("Building reference time : %s", datetime.now() - start)

	def main(self):
		try:
			print("\n.............. Translation Quality Analyzer ...................\n")
			logger.info(".............. Translation Quality Analyzer ...................")
			self.cwd = os.getcwd() + '/'
			connection = get_db()
			# self.build_reference_dic(connection)
			# self.check_quality()
			self.generate_blue()
		except Exception as e:
			print(e)
			msg = traceback.format_exc()
			logger.info(msg)


lang = input("Enter lang : ")
target_lang = input("Enter target lang : ")
domain = input("Enter domain : ")
obj = QualityAnalyzer(lang, target_lang, domain)
obj.main()
