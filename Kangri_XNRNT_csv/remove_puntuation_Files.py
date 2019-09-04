'''
Rename the usfm files in a directory based on the \id tag  
'''
import os
import re
import codecs
import pdb

files = os.listdir("./.")

for file in files:
    try:
        if(file.split(".")[-1].lower()=="csv"):
            for line in file:
                print(line)

            # f=codecs.open(file, mode='rb', encoding="utf-8")
            # fc = f.read()
            # f_id=re.search("\\\\id\s+(.{3})", fc, re.U)
            # os.rename(file, getBookNum(f_id.group(1)) + "-" + str(f_id.group(1)) + ".usfm")
            # f.close()
    except Exception as e:
        # pdb.set_trace()
        print(file, e.message)
        pass
