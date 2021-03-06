import arcpy
import pythonaddins


#!/usr/bin/env python
# -*- coding: utf-8 -*-

#####################################################################################################################################
##                                                                                                                                 ##
##    Skrypt eksportujacy dane do DownloadManager CBDG i zasilajacy Baza4 i Oracle                                                 ##   
##                                                                                                                                 ##
##    do dzialania potrzebne:                                                                                                      ##   
##        - zainstalowany ArcMap i Python 2.7                                                                                      ##  
##        - katalog D:\_exportDM\, a w nim: projekt ARCIMS_DM.mxd                                                                  ##
##        - polaczenia do baz danych Oracle i Baza4                                                                                ##   
##        - dostep do serwera SEJSMIKA 192.168.1.74 i zmapowany lokalnie katalog DMFILEDIR (najlepiej zmapowanie pod G:\)          ##  
##                                                                                                                                 ##   
##    wywolanie wszystkich funkcji jest na samym dole tego skryptu                                                                 ##
##                                                                                                                                 ## 
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
import shutil


class CBDG(object):
    """Implementation for addins_addin.btn1 (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        ### definicja katalogu, plikow polaczenia do bazy, projektu mxd
        myPath = "D:\\_exportDM\\"
        oracleConnector = myPath + "oracle_dzaw.sde"
        baza4Connector = myPath + "baza4_dzaw.sde"
        oracleGISPIG2Connector = myPath + "oracle_gis_pig2.sde"
        mxd = arcpy.mapping.MapDocument(myPath+"ARCIMS_DM.mxd")
        layers = arcpy.mapping.ListLayers(mxd)
        
        def createMDB(tempdb_name):
            tmpDatabase = myPath+tempdb_name
            if os.path.exists(tmpDatabase):
                arcpy.Delete_management(tmpDatabase) #os.remove(tmpDatabase)
            arcpy.CreatePersonalGDB_management(myPath, tempdb_name)
        
        
        def createGDB(tempdb_name):
            tmpDatabase = myPath+tempdb_name
            if os.path.exists(tmpDatabase):
                arcpy.Delete_management(tmpDatabase) #os.remove(tmpDatabase)
            arcpy.CreateFileGDB_management(myPath, tempdb_name)
        
        #createMDB("midas.mdb")
        createGDB("midas.gdb")
        createGDB("oracle2oracle.gdb")
        
        ### allows overwrite output to SHP
        arcpy.env.overwriteOutput = True
        
        ### do tworzenia nazw z data
        now = datetime.datetime.now()
        today = datetime.datetime.now()
        yesterday = today - datetime.timedelta(days=1)   
        today = today.strftime("%d.%m.%Y")
        today_ = now.strftime("%Y_%m_%d")
        yesterday = yesterday.strftime("%d.%m.%Y")
        
        ### do zapisywania logow
        import logging
        logging.basicConfig(filename=myPath+'arcims_dm.log',level=logging.DEBUG,format='%(message)s')
        logging.info('\n*** LOG: ' + now.strftime("%Y/%m/%d %H:%M:%S") + ' ***')
        logging.info('-- Task started')
        
        ### utworzenie nazw warstw
        def create_date_name(lyrNr):
            global featureLayer
            global eksportName
            global eksportNameSHP
            
            featureLayer = layers[lyrNr]
        
            arcpy.AddMessage('  --> Nazwa warstwy: '+ str(featureLayer))
            logging.info('-- Nazwa warstwy: ' + str(featureLayer))
            
            eksportName = str(featureLayer) + "_" + now.strftime("%Y_%m_%d")
            eksportNameSHP = str(featureLayer) + "_" + now.strftime("%Y_%m_%d") + ".shp"
            arcpy.AddMessage('  --> Eksport do warstwy: '+ eksportNameSHP)
            logging.info('-- Eksport do warstwy: ' + eksportNameSHP)
            
            return (featureLayer, eksportName, eksportNameSHP)
        
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
            logging.info('-- Katalog: ' + SHPdirectory)
            return SHPdirectory
        
        
        ### FUNKCJE POMOCNICZE DO TESTOW OTWOROW
        # wybranie kilku obiektow otworow - SELECT DO TESTOW zeby nie eksportowac wszystkich kilku tysiecy
        def selectObj():
            mylayer = layers[1]
            midas_mdb = myPath+"midas.gdb\\cbdg_otwory_"+now.strftime("%Y_%m_%d")
            arcpy.Select_analysis(mylayer,out_feature_class=midas_mdb,where_clause="OTWORYPROD.W_OTWORY_MSSQL_Features.ID_CBDG < 2027") # <2025 - wybierze okolo 20
            print("/ wybrano kilka otworow do testow /") 
        
        
        ### eksport warstwy do shp
        def export2_shp(featureLayer, SHPdirectory, eksportNameSHP):
            # eksport -> SHP
            #arcpy.FeatureClassToFeatureClass_conversion (featureLayer, SHPdirectory, eksportNameSHP) 
            
            if (str(featureLayer) == "cbdg_midas_obszary"):
                global cbdg_midas_obszary
                arcpy.AddMessage('  --> Przetwarzanie cbdg_midas_obszary ')
                logging.info('Przetwarzanie cbdg_midas_obszary')
                
                cbdg_midas_obszary = layers[3] # "cbdg_midas_obszary"
                cbdg_midas_obszary__1_ = "cbdg_midas_obszary_"+now.strftime("%Y_%m_%d")
                midas_mdb = myPath+"midas.gdb"
                cbdg_midas_obszary__2_ = myPath+"midas.gdb\\cbdg_midas_obszary_" + now.strftime("%Y_%m_%d")
                
                # Process: Feature Class to Feature Class - cbdg_midas_obszary #MIDAS_GIS.PG_OBSZARY_SDE.ID_ZLOZ IS NOT NULL AND MIDAS_GIS.W_MSSQL_OG1.NAZWA IS NOT NULL
                arcpy.FeatureClassToFeatureClass_conversion(cbdg_midas_obszary, midas_mdb, cbdg_midas_obszary__1_, "MIDAS_GIS.PG_OBSZARY_SDE.ID_ZLOZ IS NOT NULL AND MIDAS_GIS.W_MSSQL_OG1.NAZWA IS NOT NULL", "ID_ZLOZ \"ID_ZLOZ\" true true false 4 Long 0 9 ,First,#,"+oracleConnector+"\\MIDAS_GIS.PG_OBSZARY_SDE,MIDAS_GIS.PG_OBSZARY_SDE.ID_ZLOZ,-1,-1;NAZWA \"NAZWA\" true true false 511 Text 0 0 ,First,#,"+oracleConnector+"\\MIDAS_GIS.PG_OBSZARY_SDE,MIDAS_GIS.W_MSSQL_OG1.NAZWA,-1,-1;NR_W_REJES \"NR_W_REJES\" true true false 30 Text 0 0 ,First,#,"+oracleConnector+"\\MIDAS_GIS.PG_OBSZARY_SDE,MIDAS_GIS.PG_OBSZARY_SDE.NR_REF_ZR,-1,-1;STATUS_1 \"STATUS_1\" true true false 30 Text 0 0 ,First,#,"+oracleConnector+"\\MIDAS_GIS.PG_OBSZARY_SDE,MIDAS_GIS.W_MSSQL_OG1.STATUS,-1,-1;STATUS_EN \"STATUS_EN\" true true false 30 Text 0 0 ,First,#,"+oracleConnector+"\\MIDAS_GIS.PG_OBSZARY_SDE,MIDAS_GIS.W_MSSQL_OG1.STATUS_EN,-1,-1", "")
                # Process: Feature Class to Feature Class - cbdg_midas_obszary
                arcpy.FeatureClassToFeatureClass_conversion(cbdg_midas_obszary__2_, SHPdirectory, eksportNameSHP, "", "ID_ZLOZ \"ID_ZLOZ\" true true false 4 Long 0 0 ,First,#,"+cbdg_midas_obszary__2_+".ID_ZLOZ,-1,-1;NAZWA \"NAZWA\" true true false 2147483647 Text 0 0 ,First,#,"+cbdg_midas_obszary__2_+".NAZWA,-1,-1;NR_W_REJES \"NR_W_REJES\" true true false 30 Text 0 0 ,First,#,"+cbdg_midas_obszary__2_+".NR_W_REJES,-1,-1;STATUS_1 \"STATUS_1\" true true false 30 Text 0 0 ,First,#,"+cbdg_midas_obszary__2_+".STATUS_1,-1,-1;STATUS_EN \"STATUS_EN\" true true false 30 Text 0 0 ,First,#,"+cbdg_midas_obszary__2_+".STATUS_EN,-1,-1", "")
        
                cbdg_midas_obszary = SHPdirectory
                return cbdg_midas_obszary
        
            
            if (str(featureLayer) == "cbdg_midas_kontury"):
                global cbdg_midas_kontury
                arcpy.AddMessage('  --> Przetwarzanie cbdg_midas_kontury ')
                logging.info('Przetwarzanie cbdg_midas_kontury')
                
                cbdg_midas_kontury = layers[5] # "cbdg_midas_kontury"
                cbdg_midas_kontury__1_ = "cbdg_midas_kontury_"+now.strftime("%Y_%m_%d")
                midas_mdb__4_ = myPath+"midas.gdb"
                cbdg_midas_kontury__2_ = myPath+"midas.gdb\\cbdg_midas_kontury_"+now.strftime("%Y_%m_%d")
                
                # Process: Feature Class to Feature Class - cbdg_midas_kontury
                arcpy.FeatureClassToFeatureClass_conversion(cbdg_midas_kontury, midas_mdb__4_, cbdg_midas_kontury__1_, "", "UWAGI \"UWAGI\" true true false 254 Text 0 0 ,First,#,"+oracleConnector+"\\MIDAS_GIS.ZL_ZLOZA_SDE,MIDAS_GIS.ZL_ZLOZA_SDE.UWAGI,-1,-1;LOKALIZ \"LOKALIZACJA\" true true false 100 Text 0 0 ,First,#,"+oracleConnector+"\\MIDAS_GIS.ZL_ZLOZA_SDE,MIDAS_GIS.ZL_ZLOZA_SDE.LOKACJA,-1,-1;NAZWA_1 \"NAZWA_1\" true true false 240 Text 0 0 ,First,#,"+oracleConnector+"\\MIDAS_GIS.ZL_ZLOZA_SDE,MIDAS_GIS.W_MSSQL_ZLOZA.NAZWA,-1,-1;KOP \"KOP\" true true false 100 Text 0 0 ,First,#,"+oracleConnector+"\\MIDAS_GIS.ZL_ZLOZA_SDE,MIDAS_GIS.W_MSSQL_ZLOZA.KOP,-1,-1;KOP_EN \"KOP_EN\" true true false 100 Text 0 0 ,First,#,"+oracleConnector+"\\MIDAS_GIS.ZL_ZLOZA_SDE,MIDAS_GIS.W_MSSQL_ZLOZA.KOP_EN,-1,-1;NADZ_GORN \"NADZ_GORN\" true true false 1000 Text 0 0 ,First,#,"+oracleConnector+"\\MIDAS_GIS.ZL_ZLOZA_SDE,MIDAS_GIS.W_MSSQL_ZLOZA.NADZ_GORN,-1,-1;ORG_KONC \"ORG_KONC\" true true false 255 Text 0 0 ,First,#,"+oracleConnector+"\\MIDAS_GIS.ZL_ZLOZA_SDE,MIDAS_GIS.W_MSSQL_ZLOZA.ORG_KONC,-1,-1;OR_KONC_EN \"OR_KONC_EN\" true true false 100 Text 0 0 ,First,#,"+oracleConnector+"\\MIDAS_GIS.ZL_ZLOZA_SDE,MIDAS_GIS.W_MSSQL_ZLOZA.OR_KONC_EN,-1,-1;ST_ZAG \"ST_ZAG\" true true false 255 Text 0 0 ,First,#,"+oracleConnector+"\\MIDAS_GIS.ZL_ZLOZA_SDE,MIDAS_GIS.W_MSSQL_ZLOZA.ST_ZAG,-1,-1;ST_ZAG_EN \"ST_ZAG_EN\" true true false 255 Text 0 0 ,First,#,"+oracleConnector+"\\MIDAS_GIS.ZL_ZLOZA_SDE,MIDAS_GIS.W_MSSQL_ZLOZA.ST_ZAG_EN,-1,-1;ID_MIDAS \"ID_MIDAS\" true true false 8 Double 10 38 ,First,#,"+oracleConnector+"\\MIDAS_GIS.ZL_ZLOZA_SDE,MIDAS_GIS.W_MSSQL_ZLOZA.ID_MIDAS,-1,-1", "")
                # Process: Feature Class to Feature Class - cbdg_midas_kontury
                arcpy.FeatureClassToFeatureClass_conversion(cbdg_midas_kontury__2_, SHPdirectory, eksportNameSHP, "", "UWAGI \"UWAGI\" true true false 254 Text 0 0 ,First,#,"+cbdg_midas_kontury__2_+",UWAGI,-1,-1;LOKALIZ \"LOKALIZACJA\" true true false 100 Text 0 0 ,First,#,"+cbdg_midas_kontury__2_+",LOKALIZ,-1,-1;NAZWA_1 \"NAZWA_1\" true true false 240 Text 0 0 ,First,#,"+cbdg_midas_kontury__2_+",NAZWA_1,-1,-1;KOP \"KOP\" true true false 100 Text 0 0 ,First,#,"+cbdg_midas_kontury__2_+",KOP,-1,-1;KOP_EN \"KOP_EN\" true true false 100 Text 0 0 ,First,#,"+cbdg_midas_kontury__2_+",KOP_EN,-1,-1;NADZ_GORN \"NADZ_GORN\" true true false 1000 Text 0 0 ,First,#,"+cbdg_midas_kontury__2_+",NADZ_GORN,-1,-1;ORG_KONC \"ORG_KONC\" true true false 255 Text 0 0 ,First,#,"+cbdg_midas_kontury__2_+",ORG_KONC,-1,-1;OR_KONC_EN \"OR_KONC_EN\" true true false 100 Text 0 0 ,First,#,"+cbdg_midas_kontury__2_+",OR_KONC_EN,-1,-1;ST_ZAG \"ST_ZAG\" true true false 255 Text 0 0 ,First,#,"+cbdg_midas_kontury__2_+",ST_ZAG,-1,-1;ST_ZAG_EN \"ST_ZAG_EN\" true true false 255 Text 0 0 ,First,#,"+cbdg_midas_kontury__2_+",ST_ZAG_EN,-1,-1;ID_MIDAS \"ID_MIDAS\" true true false 8 Double 10 38 ,First,#,"+cbdg_midas_kontury__2_+",ID_MIDAS,-1,-1", "")
                
                cbdg_midas_kontury = SHPdirectory
                return cbdg_midas_kontury
           
            
            if (str(featureLayer) == "cbdg_midas_tereny"):
                global cbdg_midas_tereny
                arcpy.AddMessage('  --> Przetwarzanie cbdg_midas_tereny ')
                logging.info('Przetwarzanie cbdg_midas_tereny')
                cbdg_midas_tereny__1_ = "cbdg_midas_tereny_"+now.strftime("%Y_%m_%d")
                cbdg_midas_tereny = layers[4] # "cbdg_midas_kontury"
                
                midas_mdb__3_ = myPath+"midas.gdb"
                cbdg_midas_tereny__3_ = myPath+"midas.gdb\\cbdg_midas_tereny_"+now.strftime("%Y_%m_%d")
                
                # Process: Feature Class to Feature Class - cbdg_midas_tereny
                arcpy.FeatureClassToFeatureClass_conversion(cbdg_midas_tereny, midas_mdb__3_, cbdg_midas_tereny__1_, "MIDAS_GIS.W_MSSQL_TG1.NAZWA IS NOT NULL AND MIDAS_GIS.PG_TERENY_SDE.ID_ZLOZ IS NOT NULL", "NR_W_REJES \"NR_W_REJES\" true true false 30 Text 0 0 ,First,#,"+oracleConnector+"\\MIDAS_GIS.PG_TERENY_SDE,MIDAS_GIS.PG_TERENY_SDE.NR_REF_ZR,-1,-1;ID_ZLOZ \"ID_ZLOZ\" true true false 4 Long 0 9 ,First,#,"+oracleConnector+"\\MIDAS_GIS.PG_TERENY_SDE,MIDAS_GIS.PG_TERENY_SDE.ID_ZLOZ,-1,-1;NAZWA \"NAZWA\" true false false 511 Text 0 0 ,First,#,"+oracleConnector+"\\MIDAS_GIS.PG_TERENY_SDE,MIDAS_GIS.W_MSSQL_TG1.NAZWA,-1,-1;STATUS_1 \"STATUS_1\" true false false 30 Text 0 0 ,First,#,"+oracleConnector+"\\MIDAS_GIS.PG_TERENY_SDE,MIDAS_GIS.W_MSSQL_TG1.STATUS,-1,-1;STATUS_EN \"STATUS_EN\" true true false 9 Text 0 0 ,First,#,"+oracleConnector+"\\MIDAS_GIS.PG_TERENY_SDE,MIDAS_GIS.W_MSSQL_TG1.STATUS_EN,-1,-1", "")
                # Process: Feature Class to Feature Class - cbdg_midas_tereny
                arcpy.FeatureClassToFeatureClass_conversion(cbdg_midas_tereny__3_, SHPdirectory, eksportNameSHP, "", "NR_W_REJES \"NR_W_REJES\" true true false 30 Text 0 0 ,First,#,"+cbdg_midas_tereny__3_+",NR_W_REJES,-1,-1;ID_ZLOZ \"ID_ZLOZ\" true true false 4 Long 0 9 ,First,#,"+cbdg_midas_tereny__3_+",ID_ZLOZ,-1,-1;NAZWA \"NAZWA\" true false false 511 Text 0 0 ,First,#,"+cbdg_midas_tereny__3_+",NAZWA,-1,-1;STATUS_1 \"STATUS_1\" true false false 30 Text 0 0 ,First,#,"+cbdg_midas_tereny__3_+",STATUS_1,-1,-1;STATUS_EN \"STATUS_EN\" true true false 9 Text 0 0 ,First,#,"+cbdg_midas_tereny__3_+",STATUS_EN,-1,-1", "")
                
                cbdg_midas_tereny = SHPdirectory
                return cbdg_midas_tereny
        
            
            if (str(featureLayer) == "cbdg_otwory"):
                global otwory
                arcpy.AddMessage('  --> Przetwarzanie cbdg_otwory ')
                logging.info('Przetwarzanie cbdg_otwory')
                
                mylayer = layers[1]
                midas_mdb = myPath+"midas.gdb\\cbdg_otwory_"+now.strftime("%Y_%m_%d")
                arcpy.Select_analysis(mylayer,out_feature_class=midas_mdb)
                #selectObj() # wybranie kilku do testow
                
                cbdg_otwory = myPath+"midas.gdb\\cbdg_otwory_"+now.strftime("%Y_%m_%d")
                
                # Process: Feature Class to Feature Class - cbdg_otwory
                arcpy.FeatureClassToFeatureClass_conversion(cbdg_otwory, SHPdirectory, eksportNameSHP, "", "NAZWA \"NAZWA\" true false false 50 Text 0 0 ,First,#,"+cbdg_otwory+",OTWORYPROD_W_OTWORY_MSSQL_Features_NAZWA,-1,-1;GLEBOKOSC \"GLEBOKOSC\" true false false 8 Double 0 0 ,First,#,"+cbdg_otwory+",OTWORYPROD_W_OTWORY_MSSQL_Features_GLEBOKOSC,-1,-1;STRAT \"STRAT\" true true false 100 Text 0 0 ,First,#,"+cbdg_otwory+",OTWORYPROD_W_OTWORY_MSSQL_Features_STRAT,-1,-1;STRAT_EN \"STRAT_EN\" true true false 100 Text 0 0 ,First,#,"+cbdg_otwory+",OTWORYPROD_W_OTWORY_MSSQL_Features_STRAT_EN,-1,-1;CEL_WIERC \"CEL_WIERC\" true true false 25 Text 0 0 ,First,#,"+cbdg_otwory+",OTWORYPROD_W_OTWORY_MSSQL_Features_CEL_WIERC,-1,-1;CEL_W_EN \"CEL_W_EN\" true true false 25 Text 0 0 ,First,#,"+cbdg_otwory+",OTWORYPROD_W_OTWORY_MSSQL_Features_CEL_W_EN,-1,-1;ROK \"ROK\" true true false 2 Short 0 0 ,First,#,"+cbdg_otwory+",OTWORYPROD_W_OTWORY_MSSQL_Features_ROK,-1,-1;RZEDNA \"RZEDNA\" true true false 8 Double 0 0 ,First,#,"+cbdg_otwory+",OTWORYPROD_W_OTWORY_MSSQL_Features_RZEDNA,-1,-1;DL_GEO \"DL_GEO\" true true false 8 Double 0 0 ,First,#,"+cbdg_otwory+",OTWORYPROD_W_OTWORY_MSSQL_Features_DL_GEO,-1,-1;SZ_GEO \"SZ_GEO\" true true false 8 Double 0 0 ,First,#,"+cbdg_otwory+",OTWORYPROD_W_OTWORY_MSSQL_Features_SZ_GEO,-1,-1;X_92 \"X_92\" true true false 8 Double 0 0 ,First,#,"+cbdg_otwory+",OTWORYPROD_W_OTWORY_MSSQL_Features_X_92,-1,-1;Y_92 \"Y_92\" true true false 8 Double 0 0 ,First,#,"+cbdg_otwory+",OTWORYPROD_W_OTWORY_MSSQL_Features_Y_92,-1,-1;PODS_LOKA \"PODS_LOKA\" true true false 80 Text 0 0 ,First,#,"+cbdg_otwory+",OTWORYPROD_W_OTWORY_MSSQL_Features_PODS_LOKA,-1,-1;PODS_L_EN \"PODS_L_EN\" true true false 80 Text 0 0 ,First,#,"+cbdg_otwory+",OTWORYPROD_W_OTWORY_MSSQL_Features_PODS_L_EN,-1,-1;LOK_WERYF \"LOK_WERYF\" true true false 3 Text 0 0 ,First,#,"+cbdg_otwory+",OTWORYPROD_W_OTWORY_MSSQL_Features_LOK_WERYF,-1,-1;LOK_W_EN \"LOK_W_EN\" true true false 3 Text 0 0 ,First,#,"+cbdg_otwory+",OTWORYPROD_W_OTWORY_MSSQL_Features_LOK_W_EN,-1,-1;MIEJSCOWOSC \"MIEJSCOWOSC\" true true false 40 Text 0 0 ,First,#,"+cbdg_otwory+",OTWORYPROD_W_OTWORY_MSSQL_Features_MIEJSCOWOSC,-1,-1;GMINA \"GMINA\" true true false 45 Text 0 0 ,First,#,"+cbdg_otwory+",OTWORYPROD_W_OTWORY_MSSQL_Features_GMINA,-1,-1;POWIAT \"POWIAT\" true true false 40 Text 0 0 ,First,#,"+cbdg_otwory+",OTWORYPROD_W_OTWORY_MSSQL_Features_POWIAT,-1,-1;WOJEWODZTWO \"WOJEWODZTWO\" true true false 40 Text 0 0 ,First,#,"+cbdg_otwory+",OTWORYPROD_W_OTWORY_MSSQL_Features_WOJEWODZTWO,-1,-1;ARCHIWUM \"ARCHIWUM\" true true false 180 Text 0 0 ,First,#,"+cbdg_otwory+",OTWORYPROD_W_OTWORY_MSSQL_Features_ARCHIWUM,-1,-1;NR_DOK \"NR_DOK\" true true false 50 Text 0 0 ,First,#,"+cbdg_otwory+",OTWORYPROD_W_OTWORY_MSSQL_Features_NR_DOK,-1,-1;ID_CBDG \"ID_CBDG\" true false false 8 Double 0 0 ,First,#,"+cbdg_otwory+",OTWORYPROD_W_OTWORY_MSSQL_Features_ID_CBDG,-1,-1;RDZEN \"RDZEN\" true true false 2147483647 Text 0 0 ,First,#,"+cbdg_otwory+",OTWORYPROD_W_OTWORY_MSSQL_Features_RDZEN,-1,-1;BADANIE \"BADANIE\" true true false 2147483647 Text 0 0 ,First,#,"+cbdg_otwory+",OTWORYPROD_V_OTWORY_BADANIA_BADANIE,-1,-1;GEOFIZYKA \"GEOFIZYKA\" true true false 1 Text 0 0 ,First,#,"+cbdg_otwory+",OTWORYPROD_V_OTWORY_BADANIA_GEOFIZYKA,-1,-1;ANALIZY \"ANALIZY\" true true false 2147483647 Text 0 0 ,First,#,"+cbdg_otwory+",OTWORYPROD_V_OTWORY_BADANIA_ANALIZY,-1,-1", "")
                
                otwory = SHPdirectory
                return otwory
        
            if (str(featureLayer) == "cbdg_otwory_badania"):
                global otwory_badania
                arcpy.AddMessage('  --> Przetwarzanie cbdg_otwory_badania ')
                logging.info('Przetwarzanie cbdg_otwory_badania')
                
                cbdg_otwory = myPath+"midas.gdb\\cbdg_otwory_"+now.strftime("%Y_%m_%d")
                mylayer = cbdg_otwory
                midas_mdb = myPath+"midas.gdb\\cbdg_otwory_badania_"+now.strftime("%Y_%m_%d")
                arcpy.Select_analysis(mylayer,out_feature_class=midas_mdb,where_clause="OTWORYPROD_V_OTWORY_BADANIA_BADANIE NOT LIKE ' '")
                
                cbdg_otwory_badania = myPath+"midas.gdb\\cbdg_otwory_badania_"+now.strftime("%Y_%m_%d")
                
                # Process: Feature Class to Feature Class - cbdg_otwory
                arcpy.FeatureClassToFeatureClass_conversion(cbdg_otwory_badania, SHPdirectory, eksportNameSHP, "OTWORYPROD_V_OTWORY_BADANIA_BADANIE IS NOT NULL", "NAZWA \"NAZWA\" true false false 50 Text 0 0 ,First,#,"+cbdg_otwory_badania+",OTWORYPROD_W_OTWORY_MSSQL_Features_NAZWA,-1,-1;GLEBOKOSC \"GLEBOKOSC\" true false false 8 Double 0 0 ,First,#,"+cbdg_otwory_badania+",OTWORYPROD_W_OTWORY_MSSQL_Features_GLEBOKOSC,-1,-1;STRAT \"STRAT\" true true false 100 Text 0 0 ,First,#,"+cbdg_otwory_badania+",OTWORYPROD_W_OTWORY_MSSQL_Features_STRAT,-1,-1;STRAT_EN \"STRAT_EN\" true true false 100 Text 0 0 ,First,#,"+cbdg_otwory_badania+",OTWORYPROD_W_OTWORY_MSSQL_Features_STRAT_EN,-1,-1;CEL_WIERC \"CEL_WIERC\" true true false 25 Text 0 0 ,First,#,"+cbdg_otwory_badania+",OTWORYPROD_W_OTWORY_MSSQL_Features_CEL_WIERC,-1,-1;CEL_W_EN \"CEL_W_EN\" true true false 25 Text 0 0 ,First,#,"+cbdg_otwory_badania+",OTWORYPROD_W_OTWORY_MSSQL_Features_CEL_W_EN,-1,-1;ROK \"ROK\" true true false 2 Short 0 0 ,First,#,"+cbdg_otwory_badania+",OTWORYPROD_W_OTWORY_MSSQL_Features_ROK,-1,-1;RZEDNA \"RZEDNA\" true true false 8 Double 0 0 ,First,#,"+cbdg_otwory_badania+",OTWORYPROD_W_OTWORY_MSSQL_Features_RZEDNA,-1,-1;DL_GEO \"DL_GEO\" true true false 8 Double 0 0 ,First,#,"+cbdg_otwory_badania+",OTWORYPROD_W_OTWORY_MSSQL_Features_DL_GEO,-1,-1;SZ_GEO \"SZ_GEO\" true true false 8 Double 0 0 ,First,#,"+cbdg_otwory_badania+",OTWORYPROD_W_OTWORY_MSSQL_Features_SZ_GEO,-1,-1;X_92 \"X_92\" true true false 8 Double 0 0 ,First,#,"+cbdg_otwory_badania+",OTWORYPROD_W_OTWORY_MSSQL_Features_X_92,-1,-1;Y_92 \"Y_92\" true true false 8 Double 0 0 ,First,#,"+cbdg_otwory_badania+",OTWORYPROD_W_OTWORY_MSSQL_Features_Y_92,-1,-1;PODS_LOKA \"PODS_LOKA\" true true false 80 Text 0 0 ,First,#,"+cbdg_otwory_badania+",OTWORYPROD_W_OTWORY_MSSQL_Features_PODS_LOKA,-1,-1;PODS_L_EN \"PODS_L_EN\" true true false 80 Text 0 0 ,First,#,"+cbdg_otwory_badania+",OTWORYPROD_W_OTWORY_MSSQL_Features_PODS_L_EN,-1,-1;LOK_WERYF \"LOK_WERYF\" true true false 3 Text 0 0 ,First,#,"+cbdg_otwory_badania+",OTWORYPROD_W_OTWORY_MSSQL_Features_LOK_WERYF,-1,-1;LOK_W_EN \"LOK_W_EN\" true true false 3 Text 0 0 ,First,#,"+cbdg_otwory_badania+",OTWORYPROD_W_OTWORY_MSSQL_Features_LOK_W_EN,-1,-1;MIEJSCOWOSC \"MIEJSCOWOSC\" true true false 40 Text 0 0 ,First,#,"+cbdg_otwory_badania+",OTWORYPROD_W_OTWORY_MSSQL_Features_MIEJSCOWOSC,-1,-1;GMINA \"GMINA\" true true false 45 Text 0 0 ,First,#,"+cbdg_otwory_badania+",OTWORYPROD_W_OTWORY_MSSQL_Features_GMINA,-1,-1;POWIAT \"POWIAT\" true true false 40 Text 0 0 ,First,#,"+cbdg_otwory_badania+",OTWORYPROD_W_OTWORY_MSSQL_Features_POWIAT,-1,-1;WOJEWODZTWO \"WOJEWODZTWO\" true true false 40 Text 0 0 ,First,#,"+cbdg_otwory_badania+",OTWORYPROD_W_OTWORY_MSSQL_Features_WOJEWODZTWO,-1,-1;ARCHIWUM \"ARCHIWUM\" true true false 180 Text 0 0 ,First,#,"+cbdg_otwory_badania+",OTWORYPROD_W_OTWORY_MSSQL_Features_ARCHIWUM,-1,-1;NR_DOK \"NR_DOK\" true true false 50 Text 0 0 ,First,#,"+cbdg_otwory_badania+",OTWORYPROD_W_OTWORY_MSSQL_Features_NR_DOK,-1,-1;ID_CBDG \"ID_CBDG\" true false false 8 Double 0 0 ,First,#,"+cbdg_otwory_badania+",OTWORYPROD_W_OTWORY_MSSQL_Features_ID_CBDG,-1,-1;RDZEN \"RDZEN\" true true false 2147483647 Text 0 0 ,First,#,"+cbdg_otwory_badania+",OTWORYPROD_W_OTWORY_MSSQL_Features_RDZEN,-1,-1;BADANIE \"BADANIE\" true true false 2147483647 Text 0 0 ,First,#,"+cbdg_otwory_badania+",OTWORYPROD_V_OTWORY_BADANIA_BADANIE,-1,-1;GEOFIZYKA \"GEOFIZYKA\" true true false 1 Text 0 0 ,First,#,"+cbdg_otwory_badania+",OTWORYPROD_V_OTWORY_BADANIA_GEOFIZYKA,-1,-1;ANALIZY \"ANALIZY\" true true false 2147483647 Text 0 0 ,First,#,"+cbdg_otwory_badania+",OTWORYPROD_V_OTWORY_BADANIA_ANALIZY,-1,-1", "")
                
                otwory_badania = SHPdirectory
                return otwory_badania
        
        ### spakowanie do zip
        def shp_zip(eksportName, SHPdirectory):
            # create archive
            archive_name = os.path.expanduser(os.path.join(myPath, eksportName))
            root_dir = os.path.expanduser(os.path.join(SHPdirectory, ''))
            shutil.make_archive(archive_name, 'zip', root_dir)
            
            arcpy.AddMessage('  --> Zipped!')
            logging.info('-- Pliki spakowane do zip')
        
        
        ### update pliku Info.asp
        def update_info_asp():   
            import fileinput
            import re
            
            # linie tekstu z data do zmiany w pliku Info.asp:
            lines_to_change = [23, 26, 65, 68, 71]
            
            for line in fileinput.input(myPath+"Info.asp", inplace=True):
                if fileinput.filelineno() in lines_to_change:
                    line = re.sub(yesterday, today, line)
                print "%s" % (line),
            
            arcpy.AddMessage("  --> YESTERDAY date: " + yesterday + ' replaced to TODAY: ' + today)
            logging.info("-- YESTERDAY date: " + yesterday + ' replaced to TODAY: ' + today)
        
        
        ### skopiowanie plikow na serwer 192.168.1.74\\DMFILEDIR\
        
        def copy2_dmfiledir(eksportName):
            logging.info('-- File transfer to 192.168.1.74\\DMFILEDIR')
            
            source_path = myPath
            dest_path = r"G:\\dzaw_test\\"
            file_name = eksportName + ".zip"
            #file_name2 = "\\Info.asp"
            
            shutil.copyfile(source_path + file_name, dest_path + file_name)
            #shutil.copyfile(source_path + file_name2, dest_path + "\\Info_aktualizacja_" + today + ".asp")
            
            arcpy.AddMessage('  --> Plik: '+ file_name + ' skopiowany na 192.168.1.74\\DMFILEDIR')
            logging.info('-- Plik ' + file_name + ' skopiowany na 192.168.1.74\\DMFILEDIR')
        
        
        
        ### przejscie do strony logowania dmadmin (domyslna przegladarka)
        import webbrowser
        def openAdminConsole():
            # open page http://dm.pgi.gov.pl/dmadmin/LogOn.aspx
            webbrowser.open('http://dm.pgi.gov.pl/dmadmin/LogOn.aspx')
            arcpy.AddMessage("  --> Browser opened ")
            # login, add labels???
        
        
        ### usuniecie starych plikow
        
        def remove_old_files(old_file_path):
            if os.path.isfile(old_file_path):
                os.remove(old_file_path)
                arcpy.AddMessage('  --> Usunieto plik: '+ old_file_path)
                logging.info('-- Usunieto plik: '+ old_file_path)
            else:
                arcpy.AddMessage('  --> Nie znaleziono pliku do usuniecia')
                logging.info('-- Nie znaleziono pliku do usuniecia')
        
        ### wyslanie info na maila
        
        def send_mail_info(lyrNr):
            
            import smtplib
            from email.mime.text import MIMEText
            
            exported_layers = ''
            for x in lyrNr:
                exported_layers += "\n" + str(layers[x]) + "_" + now.strftime("%Y_%m_%d") + ".shp"
            
            exported_layers += "\n" + "cbdg_srodowisko_jaskinie" + "_" + now.strftime("%Y_%m_%d") + ".shp"
            
            msg = MIMEText("***Download Manager - export danych " +now.strftime("%Y/%m/%d %H:%M:%S") + " ***\n\nNastepujace warstwy zostaly wyeksportowane i skopiowane na serwer: 192.168.1.74\\DMFILEDIR\ : \n" + exported_layers)
            arcpy.AddMessage('  --> Tresc wiadomosci: '+ str(msg))
            
            noreplay = 'noreplay@pgi.gov.pl' 
            dzaw = 'dzaw@pgi.gov.pl'
        
            msg['Subject'] = '*** DM export danych info ***'
            msg['From'] = noreplay
            msg['To'] = dzaw
            
            # Send the message via our own SMTP server
            s = smtplib.SMTP('ex1waw.PGI.LOCAL')
            s.sendmail(noreplay, [dzaw], msg.as_string())
            s.quit()
            arcpy.AddMessage('  --> Wiadomosc wyslana')
            logging.info('-- Wiadomosc wyslana')
        
        
        
        
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
            print("rows updated " + str(i))
        
        
        ### skopiowanie warstw i stworzenie kolumny IMS, do zasilenia IMS
        def doIMS():
            global otwory499_shp
            global otwory500_shp
            arcpy.AddMessage('Do IMS [' + now.strftime("%Y/%m/%d %H:%M:%S") + ']')       
            createSHPdir(SHPdirectory, "cbdg_otwory")
            cbdg_otwory__1_ = myPath+"cbdg_otwory_"+now.strftime("%Y_%m_%d") + "\\" + "cbdg_otwory_"+now.strftime("%Y_%m_%d") + ".shp"
            
            #  Process: Copy features - cbdg_otwory do IMS
            arcpy.CopyFeatures_management(cbdg_otwory__1_, myPath+"cbdg_otwory\\cbdg_otwory.shp" )
                
            # Process: Add Field - cbdg_otwory
            cbdg_otwory_IMS = myPath+"cbdg_otwory\\cbdg_otwory.shp"
            arcpy.AddField_management(cbdg_otwory_IMS, "IMS", "LONG", "", "", "", "", "NON_NULLABLE", "NON_REQUIRED", "")
            arcpy.AddMessage('  --> Dodano kolumne IMS do cbdg_otwory.shp ')
             
            # Calculate field with arcpy.da.UpdateCursor
            #cbdg_otwory_IMS = myPath+"cbdg_otwory\\cbdg_otwory.shp"
                
            # wypelnienie kolumny IMS
            wypelnienieIMS()
            arcpy.AddMessage('  --> Wypelniono kolumne IMS ')
                
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
        
        
        ### NIESTETY TE FUNKCJE WYWALAJA SIE PRZY WYWOLANIU Z LINII POLECEN, TRZEBA URUCHAMIAC Z ECLIPSE
        # usuniecie i zasilenie tabel na baza4 nowymi danymi
        def delAndLoadDataBAZA4():
            now = datetime.datetime.now()
            arcpy.AddMessage('--- Przetwarzanie zasilania Baza4 [' + now.strftime("%Y/%m/%d %H:%M:%S") + '] ---')
        
            #inputs = [myPath+"\\cbdg_midas_tereny_"+today_+"\\cbdg_midas_tereny_"+today_+".shp", myPath+"\\cbdg_midas_kontury_"+today_+"\\cbdg_midas_kontury_"+today_+".shp", myPath+"\\cbdg_midas_obszary_"+today_+"\\cbdg_midas_obszary_"+today_+".shp", myPath+"\\cbdg_otwory_badania_"+today_+"\\cbdg_otwory_badania_"+today_+".shp", myPath+"\\cbdg_otwory\\cbdg_otwory.shp", myPath+"\\cbdg_otwory\\otwory499.shp", myPath+"\\cbdg_otwory\\otwory500.shp", myPath+"cbdg_srodowisko_jaskinie_"+today_+"\\cbdg_srodowisko_jaskinie_"+today_+".shp"]
            #targets = [baza4Connector+"\\sde.SDE.ZLOZA_TERENY", baza4Connector+"\\sde.SDE.ZLOZA_GRANICE", baza4Connector+"\\sde.SDE.ZLOZA_OBSZARY", baza4Connector+"\\sde.SDE.OTWORY_BADANIA", baza4Connector+"\\sde.SDE.OTWORY", baza4Connector+"\\sde.SDE.OTWORY_499", baza4Connector+"\\sde.SDE.OTWORY_500", baza4Connector+"\\sde.SDE.JASKINIE"]
            #TEST:
            inputs = [myPath+"\\cbdg_midas_tereny_"+today_+"\\cbdg_midas_tereny_"+today_+".shp"]
            targets = [baza4Connector+"\\sde.SDE.ZLOZA_TERENY1"]
            
            i = 0
            for n in inputs:
                arcpy.DeleteRows_management(targets[i])
                #print(targets[i])
                arcpy.AddMessage('      Usunieto dane z '+targets[i])  
                arcpy.Append_management(n, targets[i], "NO_TEST", "", "")
                arcpy.AddMessage('      Zasilono dane do ' + targets[i])
                i=i+1
        
        
        # usuniecie i zasilenie tabel na oracle GISPIG2 nowymi danymi z baza4
        def baza4LoadORACLE():
            now = datetime.datetime.now()
            arcpy.AddMessage('--- Przetwarzanie zasilania Oracle [' + now.strftime("%Y/%m/%d %H:%M:%S") + '] ---')
        
            inputs = [baza4Connector+"\\sde.SDE.ZLOZA_GRANICE", baza4Connector+"\\sde.SDE.ZLOZA_OBSZARY", baza4Connector+"\\sde.SDE.ZLOZA_TERENY", baza4Connector+"\\sde.SDE.OTWORY"]
            temps = [myPath+"oracle2oracle.gdb\\ZLOZA_GRANICE", myPath+"oracle2oracle.gdb\\ZLOZA_OBSZARY", myPath+"oracle2oracle.gdb\\ZLOZA_TERENY", myPath+"oracle2oracle.gdb\\OTWORY"]
            targets = [oracleGISPIG2Connector+"\\GIS_PIG2.ZLOZA_GRANICE", oracleGISPIG2Connector+"\\GIS_PIG2.ZLOZA_OBSZARY", oracleGISPIG2Connector+"\\GIS_PIG2.ZLOZA_TERENY", oracleGISPIG2Connector+"\\GIS_PIG2.OTWORY"]
        
            i = 0
            for n in inputs:
                arcpy.DeleteRows_management(targets[i])
                arcpy.AddMessage('      Usunieto dane z '+targets[i])
                
                # SELECT jesli trzeba by ograniczyc do testow liczbe obiektow
                arcpy.Select_analysis(inputs[i],temps[i],"")
                arcpy.AddMessage('      Wybrano obiektow: ' + str(arcpy.GetCount_management(temps[i])))
                
                arcpy.Append_management(temps[i], targets[i], "NO_TEST", "", "")
                arcpy.AddMessage('      Zasilono dane do ' + targets[i])
                i=i+1
        
        
        # eksport danych z tabel XY do warstwy przestrzennej (w ukladzie epsg 2180)
        def xy2events2shp():
            now = datetime.datetime.now()
            arcpy.AddMessage('--- Przetwarzanie danych XY do warstwy przestrzennej .shp [' + now.strftime("%Y/%m/%d %H:%M:%S") + '] ---')
            
            inputs = [oracleConnector+"\\JASKINIEPOLSKI.V_JASKINIE"]
            fieldX = ["X_1992"]
            fieldY = ["Y_1992"]
            events = ["jaskinie_events"]
            targetPaths = ["cbdg_srodowisko_jaskinie_"+today_]
            targetNames = ["cbdg_srodowisko_jaskinie_"+today_+".shp"]  
            
            #definicja ukladu wspolrzednych - EPSG 2180 - plik szukany w domyslnym katalogu instalacyjnym arcgis
            prjFile = os.path.join(arcpy.GetInstallInfo()["InstallDir"],"Coordinate Systems/Projected Coordinate Systems/National Grids/Europe/ETRS 1989 Poland CS92.prj")
            spatialRef = arcpy.SpatialReference(prjFile)
            
            i = 0
            for n in inputs:
                createSHPdir(SHPdirectory, targetPaths[i])
                arcpy.MakeXYEventLayer_management(n, fieldX[i], fieldY[i], events[i], spatialRef, "")
                arcpy.FeatureClassToFeatureClass_conversion (events[i], myPath+targetPaths[i], targetNames[i])
                arcpy.AddMessage('  --> Wyeksportowano warstwe ' + targetNames[i])
                shp_zip(targetPaths[i], myPath+targetPaths[i])
                i=i+1
        
        
        # eksport danych z tabel XY do warstwy przestrzennej na baza4 (w ukladzie epsg 2180)
        def xy2events2baza4():
            now = datetime.datetime.now()
            arcpy.AddMessage('--- Przetwarzanie danych XY do warstwy przestrzennej na Baza4[' + now.strftime("%Y/%m/%d %H:%M:%S") + '] ---')
            
            inputs = [layers[6]] # warstwa 6 (hydro_otwory) z projektu ARCIMS_DM.mxd
            targetPaths = [baza4Connector+"\\"]
            targetNames = ["sde.SDE.HYDRO_OTWORY"]
            temps = [myPath+"oracle2oracle.gdb\\hydro_otwory"]
                
            i = 0
            for n in inputs:
                #arcpy.MakeXYEventLayer_management(n, fieldX[i], fieldY[i], events[i], spatialRef, "")        
                arcpy.Select_analysis(n,temps[i])
                arcpy.AddMessage('      Pobrano dane do ' + temps[i])
                arcpy.DeleteRows_management(targetPaths[i]+targetNames[i])
                arcpy.AddMessage('      Usunieto dane z '+targetPaths[i]+targetNames[i])
                arcpy.Append_management(temps[i], targetPaths[i]+targetNames[i], "NO_TEST", "", "")
                arcpy.AddMessage('      Zasilono dane do ' + targetPaths[i]+targetNames[i])
                i=i+1
        
        
        #####################################################################################################################################
        ##                                                                                                                                 ##
        ##    Uruchomienie kolejnych funkcji dla wybranych warstw (kolejnosc z projektu MXD)                                               ##
        ##         1 = otwory                                                                                                              ##
        ##         2 = otwory_badania                                                                                                      ## 
        ##         3 = obszary                                                                                                             ##   
        ##         4 = tereny                                                                                                              ##  
        ##         5 = kontury                                                                                                             ## 
        ##                                                                                                                                 ##
        #####################################################################################################################################
        
        ### definicja warstw do eksportu
        lyrNr = [3,4,5]
        
        arcpy.AddMessage('--- Export do .shp i .zip ---')
        for x in lyrNr:
            now = datetime.datetime.now()
            arcpy.AddMessage(str(x) + ' [' + now.strftime("%Y/%m/%d %H:%M:%S") + ']')
            create_date_name(x)
            createSHPdir(SHPdirectory, eksportName)
            export2_shp(featureLayer, SHPdirectory, eksportNameSHP)
            shp_zip(eksportName, SHPdirectory)
        
        arcpy.AddMessage('--- Kopia plikow .zip na serwer DM ---')
        for x in lyrNr:
            now = datetime.datetime.now()
            create_date_name(x)
            copy2_dmfiledir(eksportName)
            #remove_old_files("G:\\dzaw_test\\usun.txt")
        
        
        #update_info_asp()
        
        
        ### eksport warstw xy (jaskinie) do shp i kopia na serwer DM
        xy2events2shp()
        #copy2_dmfiledir("cbdg_srodowisko_jaskinie_"+today_)
        
        
        ### otworzenie konsoli adm DM i wyslanie maila z potwierdzeniem eksportu
        openAdminConsole()
        send_mail_info(lyrNr)
        
        
        ### czas wykonania
        exportTime = time.time()-startTime
        print("wykonanie wszystkiego trwalo [s]: %.2f" % round(exportTime,2))
        
        
        
        ### przygotowanie warstw do IMS i zasilenie tabel na baza4 i oracle
        doIMS()
        delAndLoadDataBAZA4()
        #baza4LoadORACLE()
        
        '''        
        ### czas wykonania
        exportTime = time.time()-startTime
        print("wykonanie wszystkiego trwalo [s]: %.2f" % round(exportTime,2))
        
        
        ### przetworzenie hydro otwory xy do warstwy przestrzennej na baza4
        lyrNr = [6]
        for x in lyrNr:
            now = datetime.datetime.now()
            arcpy.AddMessage(str(x) + ' [' + now.strftime("%Y/%m/%d %H:%M:%S") + ']')
            xy2events2baza4()
        
        
        ### czas wykonania
        totalTime = time.time()-startTime
        print("wykonanie wszystkiego trwalo [s]: %.2f" % round(totalTime,2))
        '''
        


        pass