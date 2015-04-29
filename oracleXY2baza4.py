#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('C:\\Python27\ArcGIS10.2\\lib')
sys.path.append('C:\\Python27\ArcGIS10.2\\DLLs')
sys.path.append('C:\\Python27\ArcGIS10.2\\lib\site-packages')
sys.path.append('C:\\Program Files (x86)\\ArcGIS\\Desktop10.2\\arcpy')
sys.path.append('C:\\Program Files (x86)\\ArcGIS\\Desktop10.2\\bin')
sys.path.append('C:\\Program Files (x86)\\ArcGIS\\Desktop10.2\\ArcToolbox\\Scripts')

import arcpy
import os
import datetime
import time


myPath = "D:\\_exportDM\\"
oracleConnector = myPath + "oracle_dzaw.sde"
baza4Connector = myPath + "baza4_dzaw.sde"
baza4HydroConnector = myPath + "baza4Hydro.sde"
oracle_hydro_sdo = myPath + "oracle_hydro_sdo.sde"

#mxd = arcpy.mapping.MapDocument(myPath+"ARCIMS_DM.mxd")
#layers = arcpy.mapping.ListLayers(mxd)

prjFile = os.path.join(arcpy.GetInstallInfo()["InstallDir"],"Coordinate Systems/Projected Coordinate Systems/National Grids/Europe/ETRS 1989 Poland CS92.prj")
spatialRef = arcpy.SpatialReference(prjFile)

startTime = time.time()
now = datetime.datetime.now()

def createGDB(tempdb_name):
    tmpDatabase = myPath+tempdb_name
    if os.path.exists(tmpDatabase):
        arcpy.Delete_management(tmpDatabase) #os.remove(tmpDatabase)
    arcpy.CreateFileGDB_management(myPath, tempdb_name)

createGDB("tempGDB.gdb")

arcpy.env.overwriteOutput = True


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
        arcpy.AddMessage('  --> Usuwanie danych z '+targets[i])
        arcpy.DeleteRows_management(targets[i]) 
        
        arcpy.AddMessage('  --> Kopiowanie tabeli tempTable' +tempName )
        arcpy.TableToTable_conversion(n, myPath+"tempGDB.gdb", "tempTable"+tempName)
        
        arcpy.AddMessage('  --> Tworzenie warstwy przestrzennej ' + temps[i])
        arcpy.MakeXYEventLayer_management(myPath+"tempGDB.gdb\\tempTable"+tempName, fieldX[i], fieldY[i], events[i], spatialRef, "")
        arcpy.FeatureClassToFeatureClass_conversion (events[i], myPath+"tempGDB.gdb\\", tempName)
       
        arcpy.AddMessage('  --> Zasilanie danych do ' + targets[i])
        arcpy.Append_management(temps[i], targets[i], "NO_TEST", "", "")
  
        i=i+1

def oracleXY2oracle(sourceLyr, tempName, targetLyr, X, Y):
    now = datetime.datetime.now()
    arcpy.AddMessage('--- Przetwarzanie zasilania Baza4 [' + now.strftime("%Y/%m/%d %H:%M:%S") + '] ---')

    inputs = [oracle_hydro_sdo + "\\" + sourceLyr]
    temps = [myPath + "tempGDB.gdb\\" + tempName]
    #targets = [baza4Connector + "\\" + targetLyr]
    targets = [oracle_hydro_sdo + "\\" + targetLyr]
    fieldX = [X]
    fieldY = [Y]
    events = ["tempLyr"]
    
    i = 0
    for n in inputs:
        arcpy.AddMessage('  --> Usuwanie danych z '+targets[i])
        arcpy.DeleteRows_management(targets[i]) 
        
        arcpy.AddMessage('  --> Kopiowanie tabeli tempTable' +tempName )
        arcpy.TableToTable_conversion(n, myPath+"tempGDB.gdb", "tempTable"+tempName)
        
        arcpy.AddMessage('  --> Tworzenie warstwy przestrzennej ' + temps[i])
        arcpy.MakeXYEventLayer_management(myPath+"tempGDB.gdb\\tempTable"+tempName, fieldX[i], fieldY[i], events[i], spatialRef, "")
        arcpy.FeatureClassToFeatureClass_conversion (events[i], myPath+"tempGDB.gdb\\", tempName)
       
        arcpy.AddMessage('  --> Zasilanie danych do ' + targets[i])
        arcpy.Append_management(temps[i], targets[i], "NO_TEST", "", "")
  
        i=i+1


### WYWOLANIE FUNKCJI
###oracleXY2baza4(sourceLyr, tempName, targetLyr)
#oracleXY2baza4("HYDRO.MV_MONITORING_V62", "MV_MONITORING_V62", "sde.HYDRO.HYDRO_MONITORING_test")

#oracleXY2oracle("HYDRO_SDO.MV_MWP", "MV_MWP", "HYDRO_SDO.HYDRO_MWP", "WSP_X_1992", "WSP_Y_1992")
#oracleXY2baza4("HYDRO_SDO.HYDRO_MWP", "HYDRO_MWP", "sde.HYDRO.HYDRO_MWP")

#oracleXY2oracle("HYDRO_SDO.HYDRO_MV_OTWORY", "HYDRO_MV_OTWORY", "HYDRO_SDO.HYDRO_OTWORY", "WSP1", "WSP2")
oracleXY2baza4("HYDRO_SDO.HYDRO_MV_OTWORY", "HYDRO_MV_OTWORY", "sde.HYDRO.HYDRO_OTWORY", "WSP1", "WSP2")

exportTime = time.time()-startTime
print("wykonanie wszystkiego trwalo [s]: %.2f" % round(exportTime,2))
