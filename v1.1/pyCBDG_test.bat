@Echo Off
 
Echo. 
Echo ################## Start pyCBDG TEST ################## 
Echo.  

Echo Usuwanie zmapowanego dysku G:
net use G: /delete /yes
Echo Mapowanie dysku G:
net use G: \\192.168.1.74\dmfiledir /USER:PGI\dzaw Sejsmika1234!@# /p:yes

Echo Skrypty Python:
c:\Python27\ArcGIS10.2\python.exe D:\\eclipse\\pyCBDG\\test.py %*

Echo Koniec skryptow Python

Echo. 
Echo.