import os
import shutil
import arcpy
import datetime

myPath = "D:\\_exportDM\\"
now = datetime.datetime.now()
today = datetime.datetime.now()
today_ = now.strftime("%Y_%m_%d")
yesterday = today - datetime.timedelta(days=1)
yesterday_ = yesterday.strftime("%Y_%m_%d")

#TEST  KOPIOWANIA

def copy2_dmfiledir(eksportName):
    
    source_path = myPath
    dest_path = r"G:\\test\\"
    file_name = eksportName + ".zip"
    #file_name2 = "\\Info.asp"
    
    shutil.copyfile(source_path + file_name, dest_path + file_name)
    #shutil.copyfile(source_path + file_name2, dest_path + "\\Info_aktualizacja_" + today + ".asp")
    
    #logging.info('  --> Plik ' + file_name + ' skopiowany')
    arcpy.AddMessage('  --> Plik: '+ file_name + ' skopiowany na 192.168.1.74\\DMFILEDIR')
    
#copy2_dmfiledir("test")


### TEST USUWANIE STARYCH PLIKOW

def remove_old_files(old_file_path):
    if os.path.isfile(old_file_path):
        os.remove(old_file_path)
        arcpy.AddMessage('  --> Usunieto plik: '+ old_file_path)
    else:
        arcpy.AddMessage('  --> Nie znaleziono pliku do usuniecia')


files_to_rm = ['cbdg_midas_kontury_', 'cbdg_midas_obszary_', 'cbdg_midas_tereny_', 'cbdg_otwory_', 'cbdg_otwory_badania_', 'cbdg_srodowisko_jaskinie_']

#for n in files_to_rm:
#    remove_old_files("G:\\test\\" + n + yesterday_ + ".zip")
    

# TEST regex

a = ['cbdg_midas_kontury_', 'cbdg_midas_obszary_', 'cbdg_midas_tereny_', 'cbdg_otwory_', 'cbdg_otwory_badania_', 'cbdg_srodowisko_jaskinie_']
b = [u'cbdg_midas_kontury_2015_05_11.zip', u'cbdg_midas_obszary_2015_05_11.zip', u'cbdg_midas_tereny_2015_05_11.zip', u'cbdg_otwory_2015_05_11.zip', u'cbdg_otwory_2015_05_11.zip', u'cbdg_otwory_badania_2015_05_11.zip', u'cbdg_srodowisko_jaskinie_2015_05_11.zip']

def returnMatches(a,b):
    return list(set(a) & set(b))
#print returnMatches(a,b)

import re

regex=re.compile("(cbdg_midas_kontury).*|(cbdg_midas_obszary).*|(cbdg_midas_tereny).*|(cbdg_otwory_2).*|(cbdg_otwory_badania).*|(cbdg_srodowisko_jaskinie).*")
t = [m.group(0) for b in b for m in [regex.search(b)] if m]
print t
print list(set(t))

