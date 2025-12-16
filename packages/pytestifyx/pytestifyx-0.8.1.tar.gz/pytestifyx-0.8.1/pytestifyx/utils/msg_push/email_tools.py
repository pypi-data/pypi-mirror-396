import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


from pytestifyx.utils.logs.core import log
from pytestifyx.utils.parse.config import parse_yaml_config


class EmailUtil:
    def __init__(self, email_settings=None):
        if email_settings is None:
            config = parse_yaml_config()
            self.email_settings = config['email']
            log.info(self.email_settings)

    def send_email(self, subject, body, to=None, cc=None, bcc=None, attachments=None):
        """
        发送邮件
        :param subject: 邮件主题
        :param body: 邮件正文
        :param to: 收件人
        :param cc: 抄送人
        :param bcc: 密送人
        :param attachments: 附件列表
        :return: None
        """
        log("Preparing email...")
        msg = MIMEMultipart()
        msg['From'] = self.email_settings['from']
        msg['To'] = to if to else self.email_settings['to']
        log(msg['To'])
        msg['Cc'] = ', '.join(cc) if cc else ''
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        if attachments:
            for file in attachments:
                log(f"Attaching file: {file}")
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(open(file, 'rb').read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename= {file}')
                msg.attach(part)

        recipients = [msg['To']]
        if cc:
            recipients += cc
        if bcc:
            recipients += bcc
        log(f"Recipients: {recipients}")

        try:
            server = smtplib.SMTP(self.email_settings['smtp_server'], self.email_settings['smtp_port'])
            log("Connected to SMTP server")
            server.starttls()
            server.login(self.email_settings['from'], self.email_settings['password'])
            log("Logged in to SMTP server")
            server.sendmail(self.email_settings['from'], recipients, msg.as_string())
            log("Email sent")
            server.quit()
        except Exception as e:
            log(f"Error: {e}")

    def send_simple_email(self, subject, body):
        """
        发送简单邮件
        :param subject: 邮件主题
        :param body: 邮件正文
        :return: None
        """
        self.send_email(subject, body)

    def send_email_with_cc(self, subject, body, cc):
        """
        发送带抄送的邮件
        :param subject: 邮件主题
        :param body: 邮件正文
        :param cc: 抄送人
        :return: None
        """
        self.send_email(subject, body, cc=cc)

    def send_email_with_bcc(self, subject, body, bcc):
        """
        发送带密送的邮件
        :param subject: 邮件主题
        :param body: 邮件正文
        :param bcc: 密送人
        :return: None
        """
        self.send_email(subject, body, bcc=bcc)

    def send_email_with_attachments(self, subject, body, attachments):
        """
        发送带附件的邮件
        :param subject: 邮件主题
        :param body: 邮件正文
        :param attachments: 附件列表
        :return: None
        """
        self.send_email(subject, body, attachments=attachments)


if __name__ == '__main__':
    eee = EmailUtil()
    eee.send_simple_email(subject="yapiyapi", body="yapi 接口变动")
