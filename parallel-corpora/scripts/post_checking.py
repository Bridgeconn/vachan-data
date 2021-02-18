import os
import gc
import re
import string
import traceback
import Levenshtein
import matplotlib.pyplot as plt
from pathlib import Path 
from collections import Counter, defaultdict
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer


class PostChecker:

    def __init__(self):
        self.corpora_path = ''


    def clean_text(self, text):
        text = re.sub('[“”]', '"', text)
        text = re.sub('[‘’]', "'", text)
        text = re.sub('।', '', text)
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = re.sub('\s\s+', ' ', text)
        return text.strip()
    

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


    def analyze_words_diff(self, words_diff_dic):
        print("\n........ Analyzing word differences .........\n")
        fig, ax = plt.subplots(2)
        fig_num = 0
        i = 0
        for index,lang in enumerate(words_diff_dic.keys()):
            print(lang)
            diff_freq = Counter(words_diff_dic[lang])
            print(diff_freq)
            ax[i].plot(list(diff_freq.values()), list(diff_freq.keys()), 'ro')
            ax[i].set_title(lang)
            i += 1                
            if index % 2 == 1:
                im_path = str(Path(os.getcwd()).parent) + '/images/'    
                plt.savefig(im_path+'words_diff_'+ str(fig_num) +'.png', dpi=300)    
                plt.clf()
                fig, ax = plt.subplots(2)
                fig_num += 1
                i = 0
                    

    def clean_data(self):    
        print("\n........ Cleaning data .........\n")
        for book in sorted(os.listdir(self.corpora_path)):
            for min_lang in os.listdir(self.corpora_path + book):
                lang_name = min_lang.split('_')[0]
                source_file = book + '_hindi.txt'
                target_file = book + '_' + lang_name + '.txt'
                target_file_cleaned = book + '_' + lang_name + '_cleaned.txt'
                source_file_cleaned = book + '_hindi_cleaned.txt'
                source_lines = open(self.corpora_path + book + '/' + min_lang + '/' + source_file, 'r').readlines()
                target_lines = open(self.corpora_path + book + '/' + min_lang + '/' + target_file, 'r').readlines()
                if len(source_lines) != len(target_lines):
                    print("Mismatch in number of lines.........")
                    break
                source_data = ''
                target_data = ''    
                for index,line in enumerate(source_lines):
                    s_flag = 0
                    t_flag = 0
                    t_line = target_lines[index]
                    s_text = (line.split('\t')[-1]).strip()
                    t_text = (t_line.split('\t')[-1]).strip()
                    # if re.search('\(.*\)',line):
                    #     s_flag = 1
                    # if re.search('\(.*\)',t_line):
                    #     t_flag = 1
                    # if s_flag == 1 and t_flag == 1:
                    #     if re.search('^[\(\[].*[\)\]]$', s_text.strip()):
                    #         line = re.sub('[\(\[\)\]]', '', line)
                    #     else:
                    #         line = re.sub('[\(\[].*[\)\]]','',line)        
                    #     if re.search('^[\(\[].*[\)\]]$', t_text.strip()):
                    #         t_line = re.sub('[\(\[\)\]]', '', t_line)
                    #     else:
                    #         t_line = re.sub('[\(\[].*[\)\]]','',t_line)            
                    # else:
                    #     line = re.sub('[\(\[].*[\)\]]','',line)    
                    #     t_line = re.sub('[\(\[].*[\)\]]','',t_line)    
                    line = self.clean_text(line)        
                    t_line = self.clean_text(t_line)
                    source_data += line + '\n'
                    target_data    += t_line + '\n'                    
                fp = open(self.corpora_path + book + '/' + min_lang + '/' + source_file_cleaned, 'w')    
                fp.write(source_data)
                fp.close()
                fp_t = open(self.corpora_path + book + '/' + min_lang + '/' + target_file_cleaned, 'w')    
                fp_t.write(target_data)
                fp_t.close()    
            

    def main(self):
        try:
            print("\n..................... Post checking the alignments ......................\n")
            self.corpora_path = str(Path(os.getcwd()).parent) + '/corpora/'
            self.clean_data()
            print("\n......... Processing corpora ..........\n")
            words_diff_dic = defaultdict(list)
            for book in sorted(os.listdir(self.corpora_path)):
                print("\n************************ Book : ",book, '****************************\n')
                for min_lang in os.listdir(self.corpora_path + book):
                    print("\n\nmin_lang :: ",min_lang)
                    lang_name = min_lang.split('_')[0]
                    source_file = book + '_hindi.txt'
                    target_file = book + '_' + lang_name + '.txt'
                    source_lines = open(self.corpora_path + book + '/' + min_lang + '/' + source_file, 'r').readlines()
                    target_lines = open(self.corpora_path + book + '/' + min_lang + '/' + target_file, 'r').readlines()
                    target_file_cleaned = book + '_' + lang_name + '_cleaned.txt'
                    source_file_cleaned = book + '_hindi_cleaned.txt'
                    source_lines_cleaned = open(self.corpora_path + book + '/' + min_lang + '/' + source_file_cleaned, 'r').readlines()
                    target_lines_cleaned = open(self.corpora_path + book + '/' + min_lang + '/' + target_file_cleaned, 'r').readlines()
                    post_file = book + '_' + lang_name + '_checked.txt'
                    if len(source_lines) != len(target_lines):
                        # print("Mismatch in number of lines.........")
                        break
                    data = ''
                    temp = []    
                    for index,s_line in enumerate(source_lines_cleaned):
                        s_line = s_line.split('\t')[-1]
                        t_line = (target_lines_cleaned[index]).split('\t')[-1]
                        words_diff  = abs(len(s_line.split()) - len(t_line.split()))
                        temp.append(words_diff)
                        if words_diff > 15:
                            # print("----------------------------------------------------------------------------------------")
                            edit_ratio = round(Levenshtein.ratio(s_line,t_line), 2)
                            cosine_score = round(self.find_cosine_similarity(s_line,t_line), 2)
                            # print("....", source_lines[index])
                            # print(">>>>", target_lines[index])
                            if cosine_score < 0.1 and edit_ratio < 0.3:
                                print(words_diff, '\t',edit_ratio, '\t', cosine_score, '\t', source_lines[index].strip(), '\t', target_lines[index].strip(), '\t','WRONG ALIGNMENT\n')
                                data += (target_lines[index]).strip() + '\t' + 'WRONG ALIGNMENT' + '\n'
                            else:
                                print(words_diff, '\t',edit_ratio, '\t', cosine_score, '\t', source_lines[index].strip(), '\t', target_lines[index].strip(), '\t', 'CORRECT ALIGNMENT\n')
                                data += target_lines[index]     
                        else:
                            data += target_lines[index]        
                    fp = open(self.corpora_path + book + '/' + min_lang + '/' + post_file, 'w')    
                    fp.write(data)
                    fp.close()
                    if lang_name not in words_diff_dic:
                        words_diff_dic[lang_name] = temp
                    else:
                        words_diff_dic[lang_name] += temp                    
            self.analyze_words_diff(words_diff_dic)                
        except Exception as e:
            print(e)
            traceback.print_exc()


obj = PostChecker()
obj.main()
