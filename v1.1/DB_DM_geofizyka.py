#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('C:\\Python27\ArcGIS10.2\\lib')
sys.path.append('C:\\Python27\ArcGIS10.2\\DLLs')
sys.path.append('C:\\Python27\ArcGIS10.2\\lib\site-packages')
sys.path.append('C:\\Program Files (x86)\\ArcGIS\\Desktop10.2\\arcpy')
sys.path.append('C:\\Program Files (x86)\\ArcGIS\\Desktop10.2\\bin')
sys.path.append('C:\\Program Files (x86)\\ArcGIS\\Desktop10.2\\ArcToolbox\\Scripts')
sys.path.append('C:\\Python27\\Lib\\site-packages\\')

import time
startTime = time.time()

import datetime
#startTime = datetime.datetime.now()

import arcpy
import os
import shutil


### definicja katalogu, plikow polaczenia do bazy, projektu mxd
myPath = "D:\\_exportDM\\"
oracleConnector = myPath + "oracle_dzaw.sde"
baza4Connector = myPath + "baza4_dzaw.sde"
oracleGISPIG2Connector = myPath + "oracle_gis_pig2.sde"

prjFile = os.path.join(arcpy.GetInstallInfo()["InstallDir"],"Coordinate Systems/Projected Coordinate Systems/National Grids/Europe/ETRS 1989 Poland CS92.prj")
spatialRef = arcpy.SpatialReference(prjFile)

def createGDB(tempdb_name):
    tmpDatabase = myPath+tempdb_name
    if os.path.exists(tmpDatabase):
        arcpy.Delete_management(tmpDatabase) #os.remove(tmpDatabase)
    arcpy.CreateFileGDB_management(myPath, tempdb_name)
    arcpy.AddMessage('  --> Utworzono baze gdb ' + tempdb_name)

createGDB("geofizykaGDB.gdb")

### allows overwrite output to SHP
arcpy.env.overwriteOutput = True

### do tworzenia nazw z data
now = datetime.datetime.now()
today = datetime.datetime.now()
yesterday = today - datetime.timedelta(days=1)   
today = today.strftime("%d.%m.%Y")
today_ = now.strftime("%Y_%m_%d")
yesterday = yesterday.strftime("%d.%m.%Y")

### WYWOLANIE FUNKCJI
###oracleXY2baza4(sourceLyr, tempName, targetLyr)

def oracleXY2oracle(sourceLyr, tempName, targetLyr, X, Y):
    now = datetime.datetime.now()
    arcpy.AddMessage('--- Przetwarzanie zasilania Oracle [' + now.strftime("%Y/%m/%d %H:%M:%S") + '] ---')

    inputs = [oracleConnector + "\\" + sourceLyr]
    temps = [myPath + "geofizykaGDB.gdb\\" + tempName]
    targets = [oracleGISPIG2Connector + "\\" + targetLyr]
    fieldX = [X]
    fieldY = [Y]
    events = ["tempLyr"]
    
    i = 0
    for n in inputs:
               
        arcpy.AddMessage('  --> Kopiowanie tabeli tempTable' +tempName )
        arcpy.TableToTable_conversion(n, myPath+"geofizykaGDB.gdb", "tempTable"+tempName)
        
        arcpy.AddMessage('  --> Tworzenie warstwy przestrzennej ' + temps[i])
        arcpy.MakeXYEventLayer_management(myPath+"geofizykaGDB.gdb\\tempTable"+tempName, fieldX[i], fieldY[i], events[i], spatialRef, "")
        arcpy.FeatureClassToFeatureClass_conversion (events[i], myPath+"geofizykaGDB.gdb\\", tempName)
        
        arcpy.AddMessage('  --> Usuwanie danych z '+targets[i])
        #arcpy.DeleteRows_management(targets[i]) # cos na oraclu nie przyjmuje tego narzedzia
        arcpy.TruncateTable_management(targets[i])
       
        arcpy.AddMessage('  --> Zasilanie danych do ' + targets[i])
        arcpy.Append_management(temps[i], targets[i], "NO_TEST", "", "")
        
        i=i+1

def geofizyka2baza4():
    now = datetime.datetime.now()
    arcpy.AddMessage('--- Przetwarzanie zasilania Baza4 - geofizyka [' + now.strftime("%Y/%m/%d %H:%M:%S") + '] ---')
    
    inputs = [oracleGISPIG2Connector + "\\GIS_PIG2.GEOFIZ_MAG_DELTA_T", oracleGISPIG2Connector + "\\GIS_PIG2.GEOFIZ_MAG_DELTA_Z", oracleGISPIG2Connector + "\\GIS_PIG2.GEOFIZ_MAG_AERO"]
    targets = [baza4Connector + "\\SDE.GEOFIZ_PKT_MAGNETYKA"]
    
    arcpy.AddMessage('  --> Usuwanie danych z '+targets[0])
    arcpy.DeleteRows_management(targets[0])
        
    i = 0
    for n in inputs:       
        arcpy.AddMessage('  --> Zasilanie danych do ' + targets[0])
        arcpy.Append_management(inputs[i], targets[0], "NO_TEST", "", "")
        
        i=i+1



def create_date_name():
    global eksportName
    global eksportNameSHP
    
    eksportName = "cbdg_geofizyka_mag_" + now.strftime("%Y_%m_%d")
    eksportNameSHP = "cbdg_geofizyka_mag_" + now.strftime("%Y_%m_%d") + ".shp"
    
    return (eksportName, eksportNameSHP)

SHPdirectory = ''
def createSHPdir():
    global SHPdirectory
    SHPdirectory = myPath + eksportName
    if not os.path.exists(SHPdirectory):
        os.makedirs(SHPdirectory)
    arcpy.AddMessage('  --> Katalog: '+ SHPdirectory)
    return SHPdirectory

def export2_shp(SHPdirectory, eksportNameSHP):
    # eksport -> SHP
    arcpy.AddMessage('  --> Eksportowanie do shp: '+ eksportNameSHP)
    arcpy.FeatureClassToFeatureClass_conversion(baza4Connector + "\\SDE.GEOFIZ_PKT_MAGNETYKA", SHPdirectory, eksportNameSHP)


def shp_zip(eksportName, SHPdirectory):
    # create archive
    archive_name = os.path.expanduser(os.path.join(myPath, eksportName))
    root_dir = os.path.expanduser(os.path.join(SHPdirectory, ''))
    shutil.make_archive(archive_name, 'zip', root_dir)
    
    arcpy.AddMessage('  --> Pliki spakowane do zip')


def copy2_dmfiledir(eksportName):
    
    source_path = myPath
    dest_path = r"G:\\"
    file_name = eksportName + ".zip"
    #file_name2 = "\\Info.asp"
    
    shutil.copyfile(source_path + file_name, dest_path + file_name)
    #shutil.copyfile(source_path + file_name2, dest_path + "\\Info_aktualizacja_" + today + ".asp")
    
    arcpy.AddMessage('  --> Plik: '+ file_name + ' skopiowany na 192.168.1.74\\DMFILEDIR')


from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Firefox()

DMlayers = []

def openLogin():
    driver.get("http://dm.pgi.gov.pl/dmadmin/LogOn.aspx")
    elem = driver.find_element_by_name("tbxLogin")
    elem.send_keys("dzaw")
    elem = driver.find_element_by_name("iptHaslo")
    elem.send_keys("R_ZOr3X123")
    elem.send_keys(Keys.RETURN)


def fillNames():  
    openLogin() # konsola czesto wylogowuje co powoduje bledy dlatego otwieram logowanie co warstwe
    elem = driver.find_element_by_name("btnPlikiBezOpisu")
    elem.send_keys(Keys.RETURN)
        
    elem = driver.find_element_by_id("Repeater1_ctl00_lblNazwa")
    filename = elem.get_attribute("innerHTML")
    elem = driver.find_element_by_name("Repeater1$ctl00$btnEdytuj")
    elem.send_keys(Keys.RETURN)
    print filename

    if "geofizyka_mag" in filename:
        elem = driver.find_element_by_name("iptOpis")
        elem.send_keys(u'Geofizyka - magnetyka (shp)')
        elem = driver.find_element_by_name("iptOpis_en")
        elem.send_keys("Geophysics - magnetics (shp)")
        elem.send_keys(Keys.RETURN)
        DMlayers.append(filename)
        arcpy.AddMessage('  --> Dodano opis DM MIDAS - geofizyka magnetyka..')

    

### run oracle db feed:

oracleXY2oracle("GEOFIZYKA.V_MAG_AERO_MSSQL", "V_MAG_AERO_oracle", "GIS_PIG2.GEOFIZ_MAG_AERO", "Y_1992", "X_1992")
exportTime = time.time()-startTime
#print("wykonanie trwalo [s]: %.2f" % round(exportTime,2))

oracleXY2oracle("GEOFIZYKA.V_MAG_DELTA_T_MSSQL", "V_MAG_DELTA_T_oracle", "GIS_PIG2.GEOFIZ_MAG_DELTA_T", "Y_1992", "X_1992")
exportTime = time.time()-startTime
#print("wykonanie trwalo [s]: %.2f" % round(exportTime,2))

oracleXY2oracle("GEOFIZYKA.V_MAG_DELTA_Z_MSSQL", "V_MAG_DELTA_Z_oracle", "GIS_PIG2.GEOFIZ_MAG_DELTA_Z", "Y_1992", "X_1992")
exportTime = time.time()-startTime
#print("wykonanie trwalo [s]: %.2f" % round(exportTime,2))


### run baza4 db feed:   
geofizyka2baza4()
exportTime = time.time()-startTime
#print("wykonanie trwalo [s]: %.2f" % round(exportTime,2))


### run shp export
create_date_name()
createSHPdir()
export2_shp(SHPdirectory, eksportNameSHP)
shp_zip(eksportName, SHPdirectory)

### copy 2 dmfiledir & add name in dm admin
copy2_dmfiledir(eksportName)

while len( list(set(DMlayers)) ) != 6:
    try:
        fillNames()
    except: pass

driver.close()

print("wykonanie trwalo [s]: %.2f" % round(exportTime,2))