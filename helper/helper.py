"""
Generate JSON file for client based on OpenAPI
"""
import json
import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any
import jinja2
from fastapi import Depends
from pydantic import EmailStr
from core import config

settings: config.Settings = config.get_setting()
file_path: Path = Path("." + settings.OPENAPI_FILE_PATH)
TELEPHONE_REGEX: str = r"\(?\+[0-9]{1,3}\)? ?-?[0-9]{1,3} ?-?[0-9]{3,5}?-?" \
                       r"[0-9]{4}( ?-?[0-9]{3})? ?(\w{1,10}\s?\d{1,6})?"
password_regex: str = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?" \
                      r"[#?!@$%^&*-]).{8,14}$"


async def update_json(
        setting: config.Settings = Depends(config.get_setting)) -> None:
    """
    Generate OpenAPI JSON file
    :return: None
    :rtype: NoneType
    """
    openapi_content: dict = json.loads(
        file_path.read_text(encoding=setting.ENCODING))
    for key, path_data in openapi_content["paths"].items():
        if key == '/':
            continue
        for operation in path_data.values():
            tag: str = operation["tags"][0]
            operation_id: str = operation["operationId"]
            to_remove: str = f"{tag}-"
            # new_operation_id = operation_id[len(to_remove):]
            new_operation_id = operation_id.removeprefix(to_remove)
            operation["operationId"] = new_operation_id
    # print(json.dumps(openapi_content, indent=4))
    file_path.write_text(
        json.dumps(openapi_content), encoding=setting.ENCODING)


async def render_template(template_path: str, **kwargs) -> str:
    """
    Renders a Jinja template into HTML
    :param template_path: Path of the HTML Template
    :type template_path: str
    :param kwargs: Keyword arguments
    :type kwargs: dict[str, Any]
    :return: Rendered body for the found template
    :rtype: str
    """

    path_list: list[str] = template_path.split('/')
    search_path: str = path_list[0] + '/' + path_list[1] + '/'
    template: str = path_list[2]
    if not os.path.exists(template_path):
        print('No template file present:', template_path)
        sys.exit()
    loader = jinja2.FileSystemLoader(searchpath=search_path)
    template_env = jinja2.Environment(loader=loader)
    rendered_template = template_env.get_template(template)
    return rendered_template.render(**kwargs)


async def create_email(
        recipients: list[EmailStr], sender: EmailStr,
        carbon_copy: list[EmailStr] = None,
        blind_carbon_copy: list[EmailStr] = None,
        subject: str = None, body: str = None) -> str:
    """
    Creation of email based on MIME standards
    :param recipients: List of emails for To
    :type recipients: list[EmailStr]
    :param sender: Sender email
    :type sender: EmailStr
    :param carbon_copy: List of emails for CC
    :type carbon_copy: list[EmailStr]
    :param blind_carbon_copy: List of emails for BCC
    :type blind_carbon_copy: list[EmailStr]
    :param subject: Email subject
    :type subject: str
    :param body: Email body
    :type body: str
    :return: Full email message formatted
    :rtype: str
    """
    msg: MIMEMultipart = MIMEMultipart('alternative')
    msg['From'] = sender
    msg['Subject'] = subject
    msg['To'] = ','.join(recipients)
    msg['Cc'] = carbon_copy
    msg['Bcc'] = blind_carbon_copy
    msg.attach(MIMEText(body, 'html'))
    email: str = msg.as_string()
    return email


async def smtp_init(
        user: EmailStr, password: str, host: str = '127.0.0.1',
        port: int = 587) -> smtplib.SMTP:
    """
    SMTP initialization of the server.
    :param user: Sender email for login
    :type user: EmailStr
    :param password: Sender password for login
    :type password: str
    :param host: SMTP host
    :type host: str
    :param port: SMTP port
    :type port: int
    :return: Instance of SMTP Server
    :rtype: SMTP
    """
    try:
        server = smtplib.SMTP(host, port)
        server.ehlo()
        server.starttls()
        server.login(user, password)
    except smtplib.SMTPServerDisconnected as sd_exc:
        print(sd_exc)
        server = None
    except smtplib.SMTPConnectError as c_exc:
        print(c_exc)
        server = None
    return server


async def smtp_email(
        server: smtplib.SMTP, from_addr: EmailStr, to_addr: list[EmailStr],
        msg: str) -> bool:
    """
    SMTP process to send email
    :param server: Instance of SMTP server
    :type server: SMTP
    :param from_addr: From email address
    :type from_addr: EmailStr
    :param to_addr: To email addresses
    :type to_addr: list[EmailStr]
    :param msg: Message based on MIME
    :type msg: str
    :return: True if the email was sent; otherwise false
    :rtype: bool
    """
    sent: bool = False
    try:
        server.sendmail(from_addr, to_addr, msg)
        sent = True
    except smtplib.SMTPDataError as d_exc:
        print(d_exc)
    except smtplib.SMTPResponseException as r_exc:
        print(r_exc)
    server.quit()
    return sent


async def send_email(
        recipients: list[EmailStr], sender: EmailStr,
        user_email: EmailStr, user_password: str,
        carbon_copy: list[EmailStr] = None,
        blind_carbon_copy: list[EmailStr] = None, subject: str = None,
        path: str = '/', host: str = '127.0.0.1',
        port: int = 587, **kwargs: dict[str, Any]) -> bool:
    """
    Sends email using a Jinja HTML template and SMTP
    :param recipients: List of emails for To
    :type recipients: list[EmailStr]
    :param sender: Sender email
    :type sender: EmailStr
    :param user_email: Sender email for login
    :type user_email: EmailStr
    :param user_password: Sender password for login
    :type user_password: str
    :param carbon_copy: List of emails for CC
    :type carbon_copy: list[EmailStr]
    :param blind_carbon_copy: List of emails for BCC
    :type blind_carbon_copy: list[EmailStr]
    :param subject: Email subject
    :type subject: str
    :param host: SMTP host
    :type host: str
    :param port: SMTP port
    :type port: int
    :param kwargs: Keyword arguments
    :type kwargs: dict[str, Any]
    :return: True if the email was sent; otherwise false
    :rtype: bool
    """
    to_list: list[EmailStr] = recipients
    if carbon_copy:
        to_list = to_list + carbon_copy
    if blind_carbon_copy:
        to_list = to_list + blind_carbon_copy

    rendered_email: str = await render_template(template_path=path, **kwargs)
    body: bytes = rendered_email.encode("utf8")
    body_str: str = body.decode('utf-8')
    email: str = await create_email(
        to_list, sender, carbon_copy, blind_carbon_copy, subject, body_str)
    server: smtplib.SMTP = await smtp_init(
        user_email, user_password, host, port)
    sent_email: bool = False
    try:
        sent_email = await smtp_email(server, sender, to_list, email)
    except smtplib.SMTPException as exc:
        print(exc)
    return sent_email


async def send_test_email(
        email_to: EmailStr,
        setting: config.Settings = Depends(config.get_setting)
) -> bool:
    """
    Sent test email using environment vars
    :param email_to: recipient email
    :type email_to: EmailStr
    :param setting: Settings to configure email process
    :type setting: Settings
    :return: None
    :rtype: NoneType
    """
    project_name = setting.PROJECT_NAME
    subject = f"{project_name} - Test email"
    path: str = setting.EMAIL_TEMPLATES_DIR + '/' 'test_email.jinja2'
    with open(Path(setting.EMAIL_TEMPLATES_DIR) / "test_email.jinja2",
              encoding='UTF-8') as file:
        template_str = file.read()
    sent: bool = await send_email(
        [email_to], setting.SMTP_USER, setting.SMTP_USER,
        setting.SMTP_PASSWORD, subject=subject, body=template_str, path=path,
        host=setting.SMTP_HOST, project_name=setting.PROJECT_NAME,
        email=email_to)
    return sent
