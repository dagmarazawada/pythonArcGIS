#!/usr/bin/env python
# -*- coding: utf-8 -*-

#####################################################################################################################################
##                                                                                                                                 																								 ##
##    Skrypt eksportujacy dane do DownloadManager CBDG i zasilajacy Baza4 i Oracle                                                                                                  	 ##   
##                                                                                                                                                                                                                                  ##
##    do dzialania potrzebne:                                                                                                                                                                                             ##   
##        - zainstalowany ArcMap i Python 2.7                                                                                                                                                                     ##  
##        - katalog D:\_exportDM\                                                                                                                                                                                        ##
##        - polaczenia do baz danych Oracle i Baza4                                                                                                                                                            ##   
##                                                                                                                                                                                                                                  ##   
##    wywolanie wszystkich funkcji jest na samym dole tego skryptu                                                                                                                                   ##
##                                                                                                                                                                                                                                  ## 
#####################################################################################################################################


### import modulow arcpy (z ArcGIS) /czasem po restarcie odlaczaja sie od sciezek systemowych i python nie widzi modulu/
# jesli instalacja ArcGIS albo Python jest w innej lokalizacji - te sciezki nalezy poprawic
import sys
sys.path.append('C:\\Python27\ArcGIS10.2\\lib')
sys.path.append('C:\\Python27\ArcGIS10.2\\DLLs')
sys.path.append('C:\\Python27\ArcGIS10.2\\lib\site-packages')
sys.path.append('C:\\Program Files (x86)\\ArcGIS\\Desktop10.2\\arcpy')
sys.path.append('C:\\Program Files (x86)\\ArcGIS\\Desktop10.2\\bin')
sys.path.append('C:\\Program Files (x86)\\ArcGIS\\Desktop10.2\\ArcToolbox\\Scripts')

import time
startTime = time.time()

import datetime
#startTime = datetime.datetime.now()

import arcpy
import os


### definicja katalogu, plikow polaczenia do bazy, projektu mxd
myPath = "D:\\_exportDM\\"
baza4Connector = myPath + "baza4_dzaw.sde"
oracleGISPIG2Connector = myPath + "oracle_gis_pig2.sde"
oracle_gis_sdo = myPath + "oracle_gis_sdo.sde"

def createGDB(tempdb_name):
    tmpDatabase = myPath+tempdb_name
    if os.path.exists(tmpDatabase):
        arcpy.Delete_management(tmpDatabase) #os.remove(tmpDatabase)
    arcpy.CreateFileGDB_management(myPath, tempdb_name)
    arcpy.AddMessage('  --> Utworzono baze gdb ' + tempdb_name)

#createGDB("tempGDB.gdb")

### allows overwrite output to SHP
arcpy.env.overwriteOutput = True

### do tworzenia nazw z data
now = datetime.datetime.now()
today = datetime.datetime.now()
yesterday = today - datetime.timedelta(days=1)   
today = today.strftime("%d.%m.%Y")
today_ = now.strftime("%Y_%m_%d")
yesterday = yesterday.strftime("%d.%m.%Y")


# usuniecie i zasilenie tabel na oracle_sdo nowymi danymi
def loadGIS_SDO():
    now = datetime.datetime.now()
    arcpy.AddMessage('--- Przetwarzanie zasilania Oracle [' + now.strftime("%Y/%m/%d %H:%M:%S") + '] ---')

    inputs = [oracleGISPIG2Connector +"\\GIS_PIG2.ZLOZA_TERENY", oracleGISPIG2Connector+"\\GIS_PIG2.ZLOZA_OBSZARY", oracleGISPIG2Connector+"\\GIS_PIG2.ZLOZA_GRANICE"]
    targets = [oracle_gis_sdo+"\\GIS_SDO.ZLOZA_TERENY", oracle_gis_sdo+"\\GIS_SDO.ZLOZA_OBSZARY", oracle_gis_sdo+"\\GIS_SDO.ZLOZA_GRANICE"]
    
    i = 0
    for n in inputs:
        #arcpy.AddMessage('  --> Kopiowanie danych z '+inputs[i])
        #arcpy.CopyFeatures_management(n,temps[i],"","","","")

        arcpy.AddMessage('  --> Usuwanie danych z '+targets[i])
        arcpy.DeleteRows_management(targets[i])
		
        arcpy.AddMessage('  --> Zasilanie danych do ' + targets[i])
        arcpy.Append_management(n, targets[i], "NO_TEST", "", "")
        arcpy.AddMessage('  --> OK')
        i=i+1

		
loadGIS_SDO()

exportTime = time.time()-startTime
print("wykonanie wszystkiego trwalo [s]: %.2f" % round(exportTime,2))