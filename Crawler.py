import requests
import smtplib
import re
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# function return a list of A Tags with class "PostHeader"
def GetATag():
    url = "http://htqt.hust.edu.vn/en.html?start=0"

    # Get html
    raw_result_html = requests.get(url)

    # make it more readable with Beautiful Soup
    bs_result_html = BeautifulSoup(raw_result_html.text,"html.parser")

    # return A Tag with class "PostHeader"
    return bs_result_html.findAll('a',{'class':'PostHeader'})

# function return a list of href from A Tag
def GetHref(A_Tags_List):
    Href_temp = []
    for i in range(0,len(A_Tags_List)):
        href = re.findall(r"href=\"[-\w\d/.,+]*\"",str(A_Tags_List[i]))   # href="...."
        href_content = re.findall(r'/[-\w\d/.,+]*[^\"]',href[0]) #"....." without "href="

        # A "http://htqt.hust.edu.vn" before the link to comple a full active url
        href_content[0] = "http://htqt.hust.edu.vn" + href_content[0]
        Href_temp.append(href_content[0])
    return Href_temp

# function return the content of A tag
def GetContent(A_Taggs_List):
    Content_temp = []
    for i in range(0,len(A_Tags_List)):
        # get content with syntax like this: ">main_content<"
        main_content = re.findall(r">.*<",str(A_Tags_List[i]))
        # remove ">" and "<" symbols
        main_content = (main_content[0].split(">")[1]).split("<")[0]
        Content_temp.append(main_content)
    return Content_temp

# function for sending an email
def SendingMail(href_list, content_list):
    host = "smtp.gmail.com"
    port = 587

    # Sending from:
    username = input("Please type the email you want to use to send message: ")
    password = input("Please type your password: ")
    from_email = username

    # Receiver
    to_email = input("Please type your email to receive annual announcement: ")

    try:
        email_conn = smtplib.SMTP(host,port)
        email_conn.ehlo()
        email_conn.starttls()
        email_conn.login(from_email,password)
        the_msg = MIMEMultipart("alternative")

        # email's header
        the_msg['Subject'] = "Recommened topic from htqt"
        the_msg['From'] = from_email

        # html format with table
        html_txt = """\
                    <html>
                    <head> Information from <i>htqt.hust.edu.vn</i> </head>
                    <body>
                        <table border="1px blue">
                            <tr>
                                <th>Title</th> </tr>
                """
        # each link requires one row in the table
        rows = ""
        for i in range(0, len(href_list)):
            rows = rows + '''
                        <tr>
                            <td>
                                <a href="{0}" style="text-decoration:none">{1}</a>
                            </td>
                        </tr>
                    '''.format(href_list[i], content_list[i])
        html_txt = html_txt + rows + "</table>"

        # attach html file to the sending mail
        part_1 = MIMEText(html_txt, "html")
        the_msg.attach(part_1)

        # sending mail and quit
        email_conn.sendmail(from_email, to_email, the_msg.as_string())
        email_conn.quit()
    except smtplib.SMTPException:
        print("Error while sending message")

# assign a list of <a> tags to A_Tags_List variable
A_Tags_List = GetATag()

# assign a list of hrefs for each element in A_Tags_List to Href_List variable
Href_List = GetHref(A_Tags_List)

# get the content/title of each element in A_Tags_List
# adn assign it to Content_List variable
Content_List = GetContent(A_Tags_List)

# Sending email
SendingMail(Href_List, Content_List)