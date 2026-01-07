import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from os.path import basename
import requests as rq
from xlwt import Workbook

BASE_URL = 'https://remoteok.com/api/'
User_Agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
Request_header = {
    'User-Agent': User_Agent,
    'Accept-Language': 'en-US, en;q=0.5'
}


def get_job_postings():
    res = rq.get(url=BASE_URL, headers=Request_header)
    return res.json()


def output_to_xls(data):
    wb = Workbook()
    sheet = wb.add_sheet('Jobs')
    headers = list(data[0].keys())
    for i in range(0, len(headers)):
        sheet.write(0, i, headers[i])
    for i in range(0, len(data)):
        job = data[i]
        values = list(job.values())
        for x in range(0, len(values)):
            sheet.write(i+1, x, values[x])
    wb.save('remote_jobs.xls')


def send_mail(send_from, send_to, subject, text, files=None):
    assert isinstance(send_to, list)
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = ",".join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg.attach(MIMEText(text))
    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(fil.read(), Name=basename(f))
        part['Content-Disposition'] = f"attachment; filename = '{basename(f)}'"
        msg.attach(part)
    smtp = smtplib.SMTP('smtp-mail.outlook.com: 587')
    smtp.starttls()
    smtp.login(send_from, 'Krish11@7')
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()



if __name__ == '__main__':
    json = get_job_postings()[1:]
    output_to_xls(json)
    send_mail('krishchoukse1107@outlook.com',
              ['rishiswami128@gmail.com'],
              'Job Postings',
              'The attached file contains job postings.', files=['remote_jobs.xls'])
