import arcpy

def send_mail_info():
    
    arcpy.AddMessage('  --> Przygotowywanie wiadomosci e-mail..')
    
    import smtplib
    from email.mime.text import MIMEText
    
    msg = MIMEText("***Download Manager - export danych " + " ***\n\nNastepujace warstwy zostaly wyeksportowane i skopiowane na serwer: 192.168.1.74\\DMFILEDIR\ : \n")
    arcpy.AddMessage('  --> Tresc wiadomosci: '+ str(msg))
    
    noreplay = 'noreplay@pgi.gov.pl' 
    dzaw = 'dzaw@pgi.gov.pl'
    dag223 = 'dagmara.223@gmail.com'
    to = 'dzaw@pgi.gov.pl; dagmara.223@gmail.com'

    msg['Subject'] = '*** DM export danych info ***'
    msg['From'] = noreplay
    msg['To'] = to
    
    # Send the message via our own SMTP server
    s = smtplib.SMTP('ex1waw.PGI.LOCAL')
    s.sendmail(noreplay, [to], msg.as_string())
    s.quit()
    arcpy.AddMessage('  --> Wiadomosc wyslana')


send_mail_info()