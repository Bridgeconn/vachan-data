import os
import re
import gc
import copy
import traceback
import Levenshtein
import pandas as pd


class ParallelCorpora:

	def __init__(self):
		self.source_lang_path = './bible_hindi/'
		self.min_lang_path = './bible_minority/'
		self.corpora_path = ''


	def write_to_file(self, df, df_min, book, folder, min_lang_name):
		# if len(df) != len(df_min):
		# 	print("\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> mismatch")
		df.to_csv(self.corpora_path + book + '/' + folder + '/' + book+ '_hindi.txt' , header=None, index=None, sep='\t', mode='w')
		df_min.to_csv(self.corpora_path + book + '/' + folder + '/' + book + '_'+ min_lang_name + '.txt' , header=None, index=None, sep='\t', mode='w')


	def splitted_verses(self, df_s, df_m, df_min):
		try:
			df_m = df_m.astype({"Verse": int})
			m_modified_indices = []
			for index, row_s in df_s.iterrows():
				s_text = str(row_s['Text'])
				s_chapter = row_s['Chapter']
				s_verse = row_s['Verse']
				min_text = ''
				# print("...............", s_text)
				s_v_tokens = [item for item in s_text.split() if len(item) > 2]
				dic = {}
				for ind, row_m in df_m.iterrows():
					m_text = str(row_m['Text'])
					# print("////////", m_text)
					m_v_tokens = [item for item in m_text.split() if len(item) > 2]
					count = 0
					for token1 in s_v_tokens:
						temp_dic = {}
						for token2 in m_v_tokens:
							temp_dic[token2] = Levenshtein.ratio(token1,token2)
						max_ind = list(temp_dic.values()).index(max(temp_dic.values()))
						if max(temp_dic.values()) > 0.8:
							count += 1
					dic[m_text] = count
				min_text = max(dic, key=dic.get)
				# print(">>>", min_text)
				m_index = (df_m.index[(df_m['Chapter'] == s_chapter) & (df_m['Verse'] == s_verse)].tolist())[0]	
				df_min.loc[[m_index], 'Text'] = min_text
				m_modified_indices.append(m_index)
			min_indices = df_m.index.values.tolist()	
			to_delete = list(set(min_indices) - set(m_modified_indices))
			for j in to_delete:
				df_min = df_min.drop(index=j)
		except Exception as e:
			print(e)
			traceback.print_exc()
		return df_min	


	def merged_verses(self, df_s, df_m, df_source):
		try:
			df_s = df_s.astype({"Verse": str})
			s_verses = list(df_s['Verse'])
			m_verses = list(df_m['Verse'])
			missing_s_v = list(set(s_verses) - set(m_verses))
			merged_m_v = list(set(m_verses) - set(s_verses))
			for item in merged_m_v:
				temp = re.findall('\d+',item)	
				merged_ind = list(range(int(temp[0]), int(temp[1])+1))
				merged_ind = [str(item) for item in merged_ind]
				if all(i in missing_s_v for i in merged_ind): 
					# print('merging in source : ', merged_ind)
					merged_verse = ''
					loc = ''
					to_delete = []
					for index,i in enumerate(merged_ind):
						if index == 0:
							loc = i
						else:
							to_delete.append((df_s.index[df_s['Verse'] == i].tolist())[0])		
						row_text = df_s.loc[df_s['Verse'] == i, 'Text'].values[0]
						merged_verse += ' ' + row_text	
					index = (df_s.index[df_s['Verse'] == loc].tolist())[0]	
					df_source.loc[[index], 'Text'] = merged_verse
					df_source.loc[[index], 'Verse'] = item
					# print('deleting : ', to_delete)
					for j in to_delete:
						df_source = df_source.drop(index=j)
			del s_verses, m_verses, missing_s_v, merged_m_v; gc.collect()		
		except Exception as e:
			print(e)
			traceback.print_exc()	
		return df_source	


	def align_verses(self, df_source, df_min):
		try:
			groups_s = df_source.groupby(['Chapter'])
			groups_min = df_min.groupby(['Chapter'])
			for group, df_s in groups_s:
				df_m = groups_min.get_group(group)
				if len(df_s) == len(df_m):
					continue
				else:
					# print("mismatch in chapter : ", group)
					if len(df_m) < len(df_s):
						# print("min has less verses........")
						df_source = self.merged_verses(df_s, df_m, df_source)
					else:
						# print("source has less verses........")	
						df_min = self.splitted_verses(df_s, df_m, df_min)
			del groups_s, groups_min; gc.collect()					
		except Exception as e:
			print(e)
			traceback.print_exc()
		return 	df_source, df_min	
			

	def get_min_verses(self, book, df):
		try:
			for folder in os.listdir(self.min_lang_path):
				df_source = copy.deepcopy(df)
				min_lang = folder.split('_')[-1]
				min_lang_name = '_'.join(folder.split('_')[:-1])
				print(".................................................................", min_lang)
				if book not in os.listdir(self.corpora_path):
					os.mkdir(self.corpora_path + book)
				if folder not in os.listdir(self.corpora_path + book ):
					os.mkdir(self.corpora_path + book + '/' + folder)
				min_book = self.min_lang_path + folder + '/' + book + min_lang + '.csv'
				df_min = pd.read_csv(min_book)
				df_min = self.clean_column_name(df_min)
				df_min.drop(['Book'], axis=1, inplace=True)
				df_s_modified, df_m_modified = self.align_verses(df_source, df_min)
				self.write_to_file(df_s_modified, df_m_modified, book, folder, min_lang_name)
		except Exception as e:
			print(e)
			traceback.print_exc()			


	def clean_column_name(self, df):
		temp = {}
		for column in df.columns:
			temp[column] = column.strip()	
		df = df.rename(columns = temp)
		return df
				

	def main(self):
		try:
			print("\n..................... Building parallel corpora ......................\n")
			cwd = os.getcwd() + '/'
			parent_dir = '/'.join(cwd.split('/')[:-2])
			if 'corpora' not in os.listdir(parent_dir):
				os.mkdir(parent_dir + '/corpora')
			self.corpora_path = parent_dir + '/corpora/'
			self.source_lang_path = parent_dir + '/bible_hindi/'
			self.min_lang_path = parent_dir + '/bible_minority/'	
			for book in sorted(os.listdir(self.source_lang_path)):
				print("\n......................... ",book, '..........................\n')
				name = book.split('.csv')[0]
				if name not in os.listdir(self.corpora_path):
					os.mkdir(self.corpora_path + name)
				df = pd.read_csv(self.source_lang_path + book)
				df = self.clean_column_name(df)
				df.drop(['Book'], axis=1, inplace=True)
				# print("Source verses : ", len(df))
				self.get_min_verses(name, df)
		except Exception as e:
			print(e)
			traceback.print_exc()


obj = ParallelCorpora()
obj.main()
