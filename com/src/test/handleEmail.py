import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os, zipfile
from bs4 import BeautifulSoup
from com.src.test.logger import logger


def deleteFiles(result_path):
    logger.info("移除目录下所有文件：%s" % result_path)
    for i in os.listdir(result_path):
        if i == "test.log":
            continue
        path_i = os.path.join(result_path,i)
        if os.path.isfile(path_i):
            os.remove(path_i)
        else:
            deleteFiles(path_i)

def deleteResultsFiles():
    result_path = os.path.join(os.path.dirname(__file__), "results")
    # screenshots_path = os.path.join(os.path.dirname(__file__), "results","screenshots")
    resultszip_path = os.path.join(os.path.dirname(__file__), "resultszip")
    deleteFiles(result_path)
    # deleteFiles(screenshots_path)
    deleteFiles(resultszip_path)

def handleHtml(report_name="report"):
    result_path = os.path.join(os.path.dirname(__file__), "..","results","%s.html" % report_name)
    soup = BeautifulSoup(open(result_path,"r"), "html.parser")
    a = soup.findAll("div",class_="popup_window")
    for i in a:
        i.extract()
    return soup

def make_zip(source_dir,output_filename):
    zipf = zipfile.ZipFile(output_filename, 'w')
    pre_len = len(os.path.dirname(source_dir))
    for parent, dirnames, filenames in os.walk(source_dir):
        for filename in filenames:
            pathfile = os.path.join(parent, filename)
            arcname = pathfile[pre_len:].strip(os.path.sep)  # 相对路径
            zipf.write(pathfile, arcname)
    zipf.close()

def sendMail(report_name="report"):
    '''
    'gjhpbxfvvuxhdhid'
    'dxnuqtwtnqngdjbi'
    '''

    # source = os.path.join(os.path.dirname(__file__),source)
    # output = output % now_time
    # output = os.path.join(os.path.dirname(__file__),"resultszip",output)
    # make_zip(source,output)
    # sender = '2415824179@qq.com'
    # smtpserver = 'smtp.qq.com'
    # password = 'gjhpbxfvvuxhdhid'


    sender = 'newjiaozi@163.com'
    smtpserver = 'smtp.163.com'
    password = "2018oooo"

    # username = '木木'


    toList = ['849781856@qq.com','liudonglin@dongmancorp.cn']
    receiver = ", ".join(toList)
    toTo = "木木QQ<%s>, Neal<%s>" % tuple(toList)

    mail_title = report_name

    # 创建一个带附件的实例
    message = MIMEMultipart()
    message['From'] = "木木<%s>" % sender
    message['To'] = toTo
    message['Subject'] = Header(mail_title, 'utf-8')

    # 邮件正文内容
    mail_html = handleHtml(report_name)
    message.attach(MIMEText('测试结果见报告', 'plain', 'utf-8'))
    message.attach(MIMEText(mail_html, 'html', 'utf-8'))
    result_path = os.path.join(os.path.dirname(__file__), "..", "results", "%s.html" % report_name)
    try:
        smtp = smtplib.SMTP()
        # smtp = smtplib.SMTP_SSL(smtpserver)  # 注意：如果遇到发送失败的情况（提示远程主机拒接连接），这里要使用SMTP_SSL方法
        # smtp.set_debuglevel(1)
        smtp.connect(smtpserver)
        smtp.login(sender, password)
        with open(result_path, 'rb') as f:
            # 这里附件的MIME和文件名
            mime = MIMEBase('html', 'html', filename=report_name)
            # 加上必要的头信息
            mime.add_header('Content-Disposition', 'attachment', filename=('utf-8', '', "%s.html" % report_name))
            mime.add_header('Content-ID', '<0>')
            mime.add_header('X-Attachment-Id', '0')
            # 把附件的内容读进来
            mime.set_payload(f.read())
            # 用Base64编码
            encoders.encode_base64(mime)
            message.attach(mime)
        smtp.sendmail(sender, receiver.split(","), message.as_string())
        smtp.sendmail(sender,toList, message.as_string())

    except Exception:
        logger.exception("邮件发送失败！")
    else:
        logger.info("邮件发送成功！")
    finally:
        smtp.quit()


if __name__ == "__main__":
    # make_zip()
    sendMail(123,"IOS测试报告-DiscoveryPageTestcase")
    # handleHtml()