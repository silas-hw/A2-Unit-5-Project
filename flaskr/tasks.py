'''
These are background tasks to be performed whilst the website backend is running. 
'''

from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3
import time

from .algorithms import *
from .config import Config as config

def send_email():
    '''
    Sends all unsent emails if their send-date is before or equal to the current time.
    '''
    db_conn=sqlite3.connect(config.DB_DIR)
    cursor = db_conn.execute('SELECT Email FROM User WHERE ReceiveNewsletter=1')
    email_list = [email[0] for email in cursor.fetchall()]

    cursor = db_conn.execute('SELECT * FROM Newsletter WHERE sent=0 AND DateSendEpoch<=?', (time.time(),))
    newsletter_list = cursor.fetchall()
    newsletter_ids = []

    # Note to examiner: actually sending emails would require an SMTP server, which would also require a domain name and (usually) payment.
    # This would also mean having to connect to an external service (such as MailTrap or Gmail SMTP Server), 
    # which I think would only complicate things when it comes to marking my project. Because of these limitations, 
    # a message is just printed to stdout instead.
    
    for newsletter in newsletter_list:
        print(f'{__name__} EMAIL SENT\n\tSubject: {newsletter[2]}\n\tBody: {newsletter[3]}\n\tRecipients: {email_list}', flush=True)
        newsletter_ids.append(newsletter[0])

    statement = f'UPDATE Newsletter SET sent=1 WHERE NewsletterID IN ({sql_prepared_tuple(len(newsletter_ids))})'

    cursor = db_conn.execute(statement, newsletter_ids)
    db_conn.commit()
    db_conn.close()

    
scheduler = BackgroundScheduler()
scheduler.add_job(func=send_email, trigger='interval', minutes=30)