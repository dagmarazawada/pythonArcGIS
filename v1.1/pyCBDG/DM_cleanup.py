#!/usr/bin/env python
# -*- coding: utf-8 -*-

##    Skrypt usuwajacy stare pliki z katalogu _exportDM

import os
import shutil
import datetime

today = datetime.datetime.now()
yesterday = today - datetime.timedelta(days=1)
yesterday_ = yesterday.strftime("%Y_%m_%d")
weekends = today - datetime.timedelta(days=3) 
weekends_ = weekends.strftime("%Y_%m_%d")

def remove_old_files(old_file_path):
    if os.path.isfile(old_file_path):
        os.remove(old_file_path)
        print('  --> Usunieto plik: '+ old_file_path)
    else:
        print('  --> Nie znaleziono pliku do usuniecia ' + old_file_path)

def remove_old_folders(old_folder_path):
    if os.path.isdir(old_folder_path):
        shutil.rmtree(old_folder_path)
        print('  --> Usunieto folder: '+ old_folder_path)
    else:
        print('  --> Nie znaleziono folderu do usuniecia ' + old_folder_path)


### usuwanie starych plikow (z data wczorajsza lub przed weekendem)
files_to_rm = ['cbdg_midas_kontury_', 'cbdg_midas_obszary_', 'cbdg_midas_tereny_', 'cbdg_otwory_', 'cbdg_otwory_badania_', 'cbdg_srodowisko_jaskinie_']

for n in files_to_rm:
    remove_old_files("D:\\_exportDM\\" + n + yesterday_ + ".zip")
    remove_old_files("D:\\_exportDM\\" + n + weekends_ + ".zip")

for n in files_to_rm:
    remove_old_folders("D:\\_exportDM\\" + n + yesterday_)
    remove_old_folders("D:\\_exportDM\\" + n + weekends_)

print("Usunieto stare pliki i katalogi")