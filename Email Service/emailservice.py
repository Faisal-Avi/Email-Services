while 1==1:
    try:
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.mime.base import MIMEBase
        from email import encoders

        from datetime import datetime

        import cx_Oracle
        import smtplib
        import time

        con = cx_Oracle.connect('u/p@ip/orclpdb.localdomain')

        cur = con.cursor()
        cur1 = con.cursor()
        print('Searching for new email')
        time.sleep(1)

        smtpserver = {"hameemgroup.com":"erp_tz@hameemgroup.com pass nishat.hameemgroup.com 587 starttls"}

        servername = 'nishat.hameemgroup.com'
        loginuser = 'erp_tz@hameemgroup.com'
        loginpassword = 'eR1!4Fa'
        smtpport = 587

        oracle_sql = '''SELECT REPLACE(REPLACE(REPLACE(email_from, CHR(10)), CHR(13)), CHR(32)) email_from,
                            REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(email_to, CHR(10)), CHR(13)), CHR(32)) ,'n/a;', ''), '0;', ''),'n/a', '') email_to,
                            REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(email_cc, CHR(10)), CHR(13)), CHR(32)) , 'n/a;', ''), '0;', ''), 'n/a', '') email_cc,
                            REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(email_bcc, CHR(10)), CHR(13)), CHR(32)), 'n/a;', ''), '0;', ''), 'n/a', '') email_bcc,
                            email_subject,
                            email_body,
                            email_outgoing_id
                     FROM gbl_email_outgoing
                     WHERE email_status IS NULL
                     AND email_outgoing_id > 17942
                     ORDER BY email_outgoing_id'''

        cur.execute(oracle_sql)
                          
        for rec in cur:
            email_from = 'dekkoerp@dekkolegacy.com'
            email_to = ('' if rec[1] == None else str(rec[1])).split(';')
            email_cc = ('' if rec[2] == None else str(rec[2])).split(';')
            email_bcc = ('' if rec[3] == None else str(rec[3])).split(';')
            email_subject = rec[4]
            email_body = rec[5]
            email_outgoing_id = str(int(rec[6]))

            msg = MIMEMultipart()

            for emails in email_to:
                if emails.find('@') < 0:
                    email_to.remove(emails)

            for emails in email_cc:
                if emails.find('@') < 0:
                    email_cc.remove(emails)

            for emails in email_bcc:
                if emails.find('@') < 0:
                    email_bcc.remove(emails)

            msg['From'] = email_from
            msg['To'] = ';'.join(email_to)
            msg['Cc'] = ';'.join(email_cc)
            msg['Bcc'] = ';'.join(email_bcc)
            msg['Subject'] = str(email_subject)

            msg.attach(MIMEText(str(email_body), 'html'))

            text = msg.as_string()

            server = smtplib.SMTP(servername, smtpport)
            server.starttls()
            server.login(loginuser, loginpassword)

            try:
                server.sendmail(email_from, [element.strip() for element in email_to + email_cc + email_bcc], text)
                cur1.execute('UPDATE gbl_email_outgoing SET email_status = 1 , status_dttm = SYSDATE WHERE email_outgoing_id = ' + email_outgoing_id);
                con.commit()
                print(email_outgoing_id + ' Email Sent successfully')
            except:
                pass
            #except Exception as e:
                #cur1.execute('UPDATE gbl_email_outgoing SET email_status = 0 , status_dttm = SYSDATE WHERE email_outgoing_id = ' + email_outgoing_id);
                #con.commit()
                #print(email_outgoing_id + ' In Exception')
                #print(e)
            server.close()
        cur1.close()    
        cur.close()
    except Exception as e:
        pass
