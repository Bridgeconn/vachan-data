'''
Rename the usfm files in a directory based on the \id tag  
'''
import os
import re
import codecs

files = os.listdir("./.")
# punctuation marks 
# punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''

for file in files:
    try:
        if(file.split(".")[-1].lower()=="csv"):
            f=codecs.open(file, mode='rb', encoding="utf-8")
            fc = f.read()
            # print(fc)
            
            # [A-z]{3}\,\d+\,\d+\, REMOVE BOOK, CHAPTER, VERSE
            output = re.sub(r'[1-9A-Z]{3}\,\d+\,\d+', '', fc)

            # Rremove punctuation (punctuations) 
            out_line = re.sub(r''''*।,.?;:!”“’‘"\'''', '', output)
                        
            # Print string without punctuation 
            print(out_line)           
          
            f.close()
    except Exception as e:
        print(file, e.message)
        pass
