from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from datetime import datetime

import cx_Oracle
import smtplib

con = cx_Oracle.connect('bottomerp/OurSDi3RpT3#mB2@192.168.66.24/dcoproddb1')

cur = con.cursor()
cur3 = con.cursor()
cur1 = con.cursor()
cur2 = con.cursor()

smtpserver = {"dekkolegacy.com":"dekkoerp@dekkolegacy.com Dekk8985oerP# smtp.office365.com 587 starttls", "dekkogroup.com":"dekkoerp@dekkolegacy.com Dekk8985oerP# smtp.office365.com 587 starttls", "dekkoashulia.com":"erpsdi@dekkoashulia.com Erp@sdi## mail.dekkoashulia.com 465 tls", "dalbd.com":"erpsdi@dalbd.com Erp@sdi##dal mail.dalbd.com 465 tls"}

def send_email():
	while True:
		currenttime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		cur3.execute('SELECT \'dekkogroup.com\' smtp_server FROM dual')
		for rec3 in cur3:
			if rec3[0] == None or rec3[0] not in smtpserver.keys():
				continue
			else:
				try:
					loginuser, loginpassword, servername, smtpport, encryptmethod = smtpserver[rec3[0]].split()
				except Exception, e:
					print str(e) + " Domain: " + rec3[0]
					continue
				
				cur.execute('SELECT REPLACE(REPLACE(REPLACE(email_from, CHR(10)), CHR(13)), CHR(32)) email_from, \
									REPLACE(REPLACE(REPLACE(email_to, CHR(10)), CHR(13)), CHR(32)) email_to, \
									REPLACE(REPLACE(REPLACE(email_cc, CHR(10)), CHR(13)), CHR(32)) email_cc, \
									REPLACE(REPLACE(REPLACE(email_bcc, CHR(10)), CHR(13)), CHR(32)) email_bcc, \
									email_subject, \
									email_body, \
									email_outgoing_id \
							 FROM gbl_email_outgoing \
							 WHERE email_status IS NULL \
							 AND (schedule_dttm IS NULL \
								  OR schedule_dttm <= TO_DATE(\'' + currenttime + '\', \'dd/mm/yyyy hh24:mi:ss\'))')
				
				try:
					if encryptmethod in ("tls", "ssl"):
						#server = smtplib.SMTP_SSL('mail.' + rec3[0], smtpport)
						server = smtplib.SMTP_SSL(servername, smtpport)
						server.ehlo()
						server.ehlo()
						server.login(loginuser, loginpassword)
					elif encryptmethod in ("starttls"):
						#server = smtplib.SMTP('mail.' + rec3[0], smtpport)
						server = smtplib.SMTP(servername, smtpport)
						server.starttls()
						server.login(loginuser, loginpassword)
					
					for rec in cur:
						try:
							#if encryptmethod in ("starttls"):
							email_from = loginuser
							#else:
								#email_from = rec[0]
							
							email_to = ('' if rec[1] == None else str(rec[1])).split(';')
							email_cc = ('' if rec[2] == None else str(rec[2])).split(';')
							email_bcc = ('' if rec[3] == None else str(rec[3])).split(';')
							email_subject = rec[4]
							email_body = rec[5]
							email_outgoing_id = str(int(rec[6]))
							
							if email_from.find('@') < 0:
								email_from = None
							
							for emails in email_to:
								if emails.find('@') < 0:
									email_to.remove(emails)
							
							for emails in email_cc:
								if emails.find('@') < 0:
									email_cc.remove(emails)
							
							for emails in email_bcc:
								if emails.find('@') < 0:
									email_bcc.remove(emails)
							
							if email_from == None or email_to == None:
								try:
									print "Email ID: " + email_outgoing_id + " was not sent due to either from or to address is blank."
									
									cur1.execute('UPDATE gbl_email_outgoing SET email_status = \'F\', status_dttm = SYSDATE WHERE email_outgoing_id = ' + email_outgoing_id);
									con.commit()
								except Exception, e:
									print str(e) + " Email ID: " + email_outgoing_id
								
								continue
							
							print "Sending email ID: " + email_outgoing_id
							
							msg = MIMEMultipart()
							msg['From'] = email_from
							msg['To'] = ';'.join(email_to)
							msg['Cc'] = ';'.join(email_cc)
							msg['Bcc'] = ';'.join(email_bcc)
							msg['Subject'] = str(email_subject).encode('utf-8')
							
							msg.attach(MIMEText(str(email_body).encode('utf8'), 'html'))
							
							# Attachments
							cur2.execute('SELECT attachment_name, attachment_file FROM gbl_email_outgoing_attachment WHERE email_outgoing_id = ' + email_outgoing_id);
							
							for attach_rec in cur2:
								part = MIMEBase('application', "octet-stream")
								attachment_name = attach_rec[0]
								attachment_file = attach_rec[1]
								part.set_payload(attachment_file.read())
								encoders.encode_base64(part)
								part.add_header('Content-Disposition', 'attachment; filename=' + attachment_name)
								msg.attach(part)
							
							text = msg.as_string()
							
							try:
								server.sendmail(email_from, filter(None, [element.strip() for element in email_to + email_cc + email_bcc]), text)
								
								print "Email ID: " + email_outgoing_id + " sent at " + datetime.now().strftime("%d/%m/%Y %H:%M:%S")
								
								cur1.execute('UPDATE gbl_email_outgoing SET email_status = \'S\', status_dttm = SYSDATE WHERE email_outgoing_id = ' + email_outgoing_id);
								con.commit()
							except Exception, e:
								print str(e) + " Email ID1: " + email_outgoing_id
						except Exception, e:
							print str(e) + " Email ID2: " + str(int(rec[6]))
				except Exception, e:
					print str(e) + " domain: " + rec3[0]

send_email()

cur2.close()
cur1.close()
cur.close()
cur3.close()
con.close()
