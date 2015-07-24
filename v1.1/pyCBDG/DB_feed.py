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
oracleConnector = myPath + "oracle_dzaw.sde"
baza4Connector = myPath + "baza4_dzaw.sde"
oracleGISPIG2Connector = myPath + "oracle_gis_pig2.sde"
baza4HydroConnector = myPath + "baza4Hydro.sde"
oracle_hydro_sdo = myPath + "oracle_hydro_sdo.sde"
oracle_gis_sdo = myPath + "oracle_gis_sdo.sde"

prjFile = os.path.join(arcpy.GetInstallInfo()["InstallDir"],"Coordinate Systems/Projected Coordinate Systems/National Grids/Europe/ETRS 1989 Poland CS92.prj")
spatialRef = arcpy.SpatialReference(prjFile)

def createGDB(tempdb_name):
    tmpDatabase = myPath+tempdb_name
    if os.path.exists(tmpDatabase):
        arcpy.Delete_management(tmpDatabase) #os.remove(tmpDatabase)
    arcpy.CreateFileGDB_management(myPath, tempdb_name)
    arcpy.AddMessage('  --> Utworzono baze gdb ' + tempdb_name)

createGDB("tempGDB.gdb")

### allows overwrite output to SHP
arcpy.env.overwriteOutput = True

### do tworzenia nazw z data
now = datetime.datetime.now()
today = datetime.datetime.now()
yesterday = today - datetime.timedelta(days=1)   
today = today.strftime("%d.%m.%Y")
today_ = now.strftime("%Y_%m_%d")
yesterday = yesterday.strftime("%d.%m.%Y")

### utworzenie katalogu na shp
SHPdirectory = ''
def createSHPdir(SHPdir, eksportName):
    global SHPdirectory
    SHPdirectory = myPath + eksportName
    if not os.path.exists(SHPdirectory):
        os.makedirs(SHPdirectory)
    if not os.path.exists(myPath+"cbdg_otwory\\"):
        os.makedirs(myPath+"cbdg_otwory\\")
    arcpy.AddMessage('  --> Katalog: '+ SHPdirectory)
    return SHPdirectory

# te dziwne obliczenia do wypelnienia kolumny IMS, wywolanie calcIMS(!IMS!, !RDZEN!, !GLEBOKOSC!)
def calcIMS(IMS, RDZEN, GLEBOKOSC):
    if (RDZEN == ' ' and GLEBOKOSC >= 500):
        return 3
    elif (RDZEN == ' ' and GLEBOKOSC < 500):
        return 4
    elif (RDZEN != ' ' and GLEBOKOSC >= 500):
        return 1
    elif (IMS == 0):
        return 2
    else:
        return 5 # 5 bedzie oznaczac ze zadne dane nie spelnily warunkow - cos jest nie tak

### wypelnienie kolumny IMS
def wypelnienieIMS():
    cbdg_otwory_IMS = myPath+"cbdg_otwory\\cbdg_otwory.shp"
    # FUNFACT - eclipse nie rozpoznaje UpdateCursora ale i tak dziala poprawnie..
    gRows = arcpy.da.UpdateCursor(cbdg_otwory_IMS, ("IMS", "RDZEN", "GLEBOKOSC"))
    i = 0
    for row in gRows:   
        #calcIMS(row[0], row[1], row[2])
        row[0] = calcIMS(row[0], row[1], row[2])
        gRows.updateRow(row)
        i=i+1
    print("  --> rows updated: " + str(i))


### skopiowanie warstw i stworzenie kolumny IMS, do zasilenia IMS
def doIMS():
    global otwory499_shp
    global otwory500_shp
    arcpy.AddMessage('--- Przetworzenia do przegladarki IMS [' + now.strftime("%Y/%m/%d %H:%M:%S") + '] ---')       
    createSHPdir(SHPdirectory, "cbdg_otwory")
    cbdg_otwory__1_ = myPath+"cbdg_otwory_"+now.strftime("%Y_%m_%d") + "\\" + "cbdg_otwory_"+now.strftime("%Y_%m_%d") + ".shp"
    
    #  Process: Copy features - cbdg_otwory do IMS
    arcpy.AddMessage('  --> Kopiowanie cbdg_otwory.shp ')
    arcpy.CopyFeatures_management(cbdg_otwory__1_, myPath+"cbdg_otwory\\cbdg_otwory.shp" )
        
    # Process: Add Field - cbdg_otwory
    # Calculate field with arcpy.da.UpdateCursor
    cbdg_otwory_IMS = myPath+"cbdg_otwory\\cbdg_otwory.shp"
    arcpy.AddField_management(cbdg_otwory_IMS, "IMS", "LONG", "", "", "", "", "NON_NULLABLE", "NON_REQUIRED", "")
    arcpy.AddMessage('  --> Dodano kolumne [IMS] do cbdg_otwory.shp ')
        
    # wypelnienie kolumny IMS
    wypelnienieIMS()
    arcpy.AddMessage('  --> Wypelniono kolumne [IMS] ')
        
    # eksport do otwory 499 i otwory 500
    otwory500_shp = myPath+"cbdg_otwory\\otwory500.shp"
    otwory499_shp = myPath+"cbdg_otwory\\otwory499.shp"
        
    # Process: Select Layer By Attribute - clear
    #arcpy.SelectLayerByAttribute_management(cbdg_otwory_IMS, "CLEAR_SELECTION", "")
    # Process: Select - otwory 500
    arcpy.Select_analysis(cbdg_otwory_IMS, otwory500_shp, "GLEBOKOSC >=500")
    # Process: Select - otwory 499
    arcpy.Select_analysis(cbdg_otwory_IMS, otwory499_shp, "GLEBOKOSC <500")
    arcpy.AddMessage('  --> Wybrano otwory.shp po glebokosci: otwory499 i otwory500 ')
    
    return(otwory499_shp, otwory500_shp)


# usuniecie i zasilenie tabel na baza4 nowymi danymi
def delAndLoadDataBAZA4():
    now = datetime.datetime.now()
    arcpy.AddMessage('--- Przetwarzanie zasilania Baza4 [' + now.strftime("%Y/%m/%d %H:%M:%S") + '] ---')

    inputs = [myPath+"\\cbdg_midas_tereny_"+today_+"\\cbdg_midas_tereny_"+today_+".shp", myPath+"\\cbdg_midas_kontury_"+today_+"\\cbdg_midas_kontury_"+today_+".shp", myPath+"\\cbdg_midas_obszary_"+today_+"\\cbdg_midas_obszary_"+today_+".shp", myPath+"\\cbdg_otwory_badania_"+today_+"\\cbdg_otwory_badania_"+today_+".shp", myPath+"\\cbdg_otwory\\cbdg_otwory.shp", myPath+"\\cbdg_otwory\\otwory499.shp", myPath+"\\cbdg_otwory\\otwory500.shp", myPath+"midas.gdb\\jaskinieTemp"]
    targets = [baza4Connector+"\\sde.SDE.ZLOZA_TERENY", baza4Connector+"\\sde.SDE.ZLOZA_GRANICE", baza4Connector+"\\sde.SDE.ZLOZA_OBSZARY", baza4Connector+"\\sde.SDE.OTWORY_BADANIA", baza4Connector+"\\sde.SDE.OTWORY", baza4Connector+"\\sde.SDE.OTWORY_499", baza4Connector+"\\sde.SDE.OTWORY_500", baza4Connector+"\\sde.SDE.JASKINIE"]
    
    i = 0
    for n in inputs:
        arcpy.AddMessage('  --> Usuwanie danych z '+targets[i])
        arcpy.DeleteRows_management(targets[i])
        #print(targets[i])
        arcpy.AddMessage('  --> Zasilanie danych do ' + targets[i])
        arcpy.Append_management(n, targets[i], "NO_TEST", "", "")
        i=i+1


# usuniecie i zasilenie tabel na oracle GISPIG2 nowymi danymi z baza4
def baza4LoadORACLE():
    now = datetime.datetime.now()
    arcpy.AddMessage('--- Przetwarzanie zasilania Oracle [' + now.strftime("%Y/%m/%d %H:%M:%S") + '] ---')

    inputs = [baza4Connector+r"\\sde.SDE.ZLOZA_GRANICE", baza4Connector+"\\sde.SDE.ZLOZA_OBSZARY", baza4Connector+"\\sde.SDE.ZLOZA_TERENY", baza4Connector+"\\sde.SDE.OTWORY", baza4Connector+"\\sde.SDE.JASKINIE"]
    #inputs = [myPath+"\\cbdg_midas_kontury_"+today_+"\\cbdg_midas_kontury_"+today_+".shp", myPath+"\\cbdg_midas_obszary_"+today_+"\\cbdg_midas_obszary_"+today_+".shp", myPath+"\\cbdg_midas_tereny_"+today_+"\\cbdg_midas_tereny_"+today_+".shp", myPath+"\\cbdg_otwory\\cbdg_otwory.shp", myPath+"midas.gdb\\jaskinieTemp"]
    temps = [myPath+"oracle2oracle.gdb\\ZLOZA_GRANICE", myPath+"oracle2oracle.gdb\\ZLOZA_OBSZARY", myPath+"oracle2oracle.gdb\\ZLOZA_TERENY", myPath+"oracle2oracle.gdb\\OTWORY", myPath+"oracle2oracle.gdb\\JASKINIE"]
    targets = [oracleGISPIG2Connector+"\\GIS_PIG2.ZLOZA_GRANICE", oracleGISPIG2Connector+"\\GIS_PIG2.ZLOZA_OBSZARY", oracleGISPIG2Connector+"\\GIS_PIG2.ZLOZA_TERENY", oracleGISPIG2Connector+"\\GIS_PIG2.OTWORY", oracleGISPIG2Connector+"\\GIS_PIG2.JASKINIE"]

    i = 0
    for n in inputs:
        arcpy.AddMessage('  --> Usuwanie danych z '+targets[i])
        arcpy.DeleteRows_management(targets[i])
        
        arcpy.Select_analysis(inputs[i],temps[i],"")
        arcpy.AddMessage('  --> Wybrano obiektow: ' + str(arcpy.GetCount_management(temps[i])))
        
        arcpy.AddMessage('  --> Zasilanie danych do ' + targets[i])
        arcpy.Append_management(temps[i], targets[i], "NO_TEST", "", "")
        i=i+1

def loadORACLE():
    now = datetime.datetime.now()
    arcpy.AddMessage('--- Przetwarzanie zasilania Oracle [' + now.strftime("%Y/%m/%d %H:%M:%S") + '] ---')

    #inputs = [baza4Connector+r"\\sde.SDE.ZLOZA_GRANICE", baza4Connector+"\\sde.SDE.ZLOZA_OBSZARY", baza4Connector+"\\sde.SDE.ZLOZA_TERENY", baza4Connector+"\\sde.SDE.OTWORY", baza4Connector+"\\sde.SDE.JASKINIE"]
    inputs = [myPath+"\\cbdg_midas_kontury_"+today_+"\\cbdg_midas_kontury_"+today_+".shp", myPath+"\\cbdg_midas_obszary_"+today_+"\\cbdg_midas_obszary_"+today_+".shp", myPath+"\\cbdg_midas_tereny_"+today_+"\\cbdg_midas_tereny_"+today_+".shp", myPath+"\\cbdg_otwory\\cbdg_otwory.shp", myPath+"midas.gdb\\jaskinieTemp"]
    #temps = [myPath+"oracle2oracle.gdb\\ZLOZA_GRANICE", myPath+"oracle2oracle.gdb\\ZLOZA_OBSZARY", myPath+"oracle2oracle.gdb\\ZLOZA_TERENY", myPath+"oracle2oracle.gdb\\OTWORY", myPath+"oracle2oracle.gdb\\JASKINIE"]
    targets = [oracleGISPIG2Connector+"\\GIS_PIG2.ZLOZA_GRANICE", oracleGISPIG2Connector+"\\GIS_PIG2.ZLOZA_OBSZARY", oracleGISPIG2Connector+"\\GIS_PIG2.ZLOZA_TERENY", oracleGISPIG2Connector+"\\GIS_PIG2.OTWORY", oracleGISPIG2Connector+"\\GIS_PIG2.JASKINIE"]

    i = 0
    for n in inputs:
        arcpy.AddMessage('  --> Usuwanie danych z '+targets[i])
        arcpy.DeleteRows_management(targets[i])
        
        #arcpy.Select_analysis(inputs[i],temps[i],"")
        arcpy.AddMessage('  --> Wybrano obiektow: ' + str(arcpy.GetCount_management(inputs[i])))
        
        arcpy.AddMessage('  --> Zasilanie danych do ' + targets[i])
        arcpy.Append_management(inputs[i], targets[i], "NO_TEST", "", "")
        i=i+1


def oracleXY2baza4(sourceLyr, tempName, targetLyr, X, Y):
    now = datetime.datetime.now()
    arcpy.AddMessage('--- Przetwarzanie zasilania Baza4 [' + now.strftime("%Y/%m/%d %H:%M:%S") + '] ---')

    inputs = [oracle_hydro_sdo + "\\" + sourceLyr]
    temps = [myPath + "tempGDB.gdb\\" + tempName]
    #targets = [baza4Connector + "\\" + targetLyr]
    targets = [baza4HydroConnector + "\\" + targetLyr]
    fieldX = [X]
    fieldY = [Y]
    events = ["tempLyr"]
    
    i = 0
    for n in inputs:
               
        arcpy.AddMessage('  --> Kopiowanie tabeli tempTable' +tempName )
        arcpy.TableToTable_conversion(n, myPath+"tempGDB.gdb", "tempTable"+tempName)
        
        arcpy.AddMessage('  --> Tworzenie warstwy przestrzennej ' + temps[i])
        arcpy.MakeXYEventLayer_management(myPath+"tempGDB.gdb\\tempTable"+tempName, fieldX[i], fieldY[i], events[i], spatialRef, "")
        arcpy.FeatureClassToFeatureClass_conversion (events[i], myPath+"tempGDB.gdb\\", tempName)
        
        arcpy.AddMessage('  --> Usuwanie danych z '+targets[i])
        arcpy.DeleteRows_management(targets[i]) 
       
        arcpy.AddMessage('  --> Zasilanie danych do ' + targets[i])
        arcpy.Append_management(temps[i], targets[i], "NO_TEST", "", "")
  
        i=i+1

### WYWOLANIE FUNKCJI
###oracleXY2baza4(sourceLyr, tempName, targetLyr)

def oracleXY2oracle(sourceLyr, tempName, targetLyr, X, Y):
    now = datetime.datetime.now()
    arcpy.AddMessage('--- Przetwarzanie zasilania Oracle [' + now.strftime("%Y/%m/%d %H:%M:%S") + '] ---')

    inputs = [oracle_hydro_sdo + "\\" + sourceLyr]
    temps = [myPath + "tempGDB.gdb\\" + tempName]
    #targets = [baza4Connector + "\\" + targetLyr]
    targets = [oracle_hydro_sdo + "\\" + targetLyr]
    fieldX = [X]
    fieldY = [Y]
    events = ["tempLyr"]
    
    i = 0
    for n in inputs:
               
        arcpy.AddMessage('  --> Kopiowanie tabeli tempTable' +tempName )
        arcpy.TableToTable_conversion(n, myPath+"tempGDB.gdb", "tempTable"+tempName)
        
        arcpy.AddMessage('  --> Tworzenie warstwy przestrzennej ' + temps[i])
        arcpy.MakeXYEventLayer_management(myPath+"tempGDB.gdb\\tempTable"+tempName, fieldX[i], fieldY[i], events[i], spatialRef, "")
        arcpy.FeatureClassToFeatureClass_conversion (events[i], myPath+"tempGDB.gdb\\", tempName)
        
        arcpy.AddMessage('  --> Usuwanie danych z '+targets[i])
        arcpy.DeleteRows_management(targets[i]) 
       
        arcpy.AddMessage('  --> Zasilanie danych do ' + targets[i])
        arcpy.Append_management(temps[i], targets[i], "NO_TEST", "", "")
  
        i=i+1


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


#####################################################################################################################################
##                                                                                                                                                                                               									 ##
##    Wypelnienie danych w bazach MSSQL i Oracle                                                                                                                                                  		 ##
##    doIMS(), delAndLoadDataBAZA4(), baza4LoadORACLE() - funkcje ze sciezkami na sztywno (mapowanie pol itp..)                                                          ##
##    oracleXY2oracle i oracleXY2baza4 - dla warstw ktore nie potrzebuja mapowania pol itp                                                                                                  ##
##                                                                                                                                                                                                                                  ##
#####################################################################################################################################

### przygotowanie warstw do IMS i zasilenie tabel na baza4 i oracle
doIMS()
delAndLoadDataBAZA4()

# funkcja tylko dla wyeksportowanych warstw DM
#baza4LoadORACLE() #- nie wiem czemu nie dziala z tego serwera
loadORACLE()

### czas wykonania
exportTime = time.time()-startTime
print("wykonanie trwalo [s]: %.2f" % round(exportTime,2))

### WYWOLANIE FUNKCJI
###oracleXY2baza4(sourceLyr, tempName, targetLyr)
#oracleXY2baza4("HYDRO.MV_MONITORING_V62", "MV_MONITORING_V62", "sde.HYDRO.HYDRO_MONITORING_test")

oracleXY2baza4("HYDRO_SDO.HYDRO_MWP", "HYDRO_MWP", "sde.HYDRO.HYDRO_MWP", "WSP_X_1992", "WSP_Y_1992")
oracleXY2baza4("HYDRO_SDO.HYDRO_MV_OTWORY", "HYDRO_MV_OTWORY", "sde.HYDRO.HYDRO_OTWORY", "WSP1", "WSP2")

oracleXY2oracle("HYDRO_SDO.HYDRO_MV_MWP", "MV_MWP", "HYDRO_SDO.HYDRO_MWP", "WSP_X_1992", "WSP_Y_1992")
oracleXY2oracle("HYDRO_SDO.HYDRO_MV_OTWORY", "HYDRO_MV_OTWORY", "HYDRO_SDO.HYDRO_OTWORY", "WSP1", "WSP2")

#kopia MIDAS na GIS_SDO
loadGIS_SDO()

exportTime = time.time()-startTime
print("wykonanie wszystkiego trwalo [s]: %.2f" % round(exportTime,2))