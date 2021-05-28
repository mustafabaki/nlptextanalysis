
def send_email(picture, excel, email):
    """
    This function is for sending the results to the users as an email with attachment.
    @param picture: the path of the picture file
    @param excel: the path of excel file
    @param email: the email address of receiver
    """
    import os
    import smtplib
    import imghdr
    from email.message import EmailMessage

    EMAIL_ADDRESS = "nlptextanalysis@gmail.com"
    EMAIL_PASSWORD = "nlptext12345"

    files = [picture,excel]


    msg = EmailMessage()
    msg['Subject'] = 'Your NLP Text Analysis Results'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email

    msg.set_content('The WordCloud image and the excel file has been attached in the email. \n Have a good day! \n NLP Text Analysis Project')
    names = ['Wordcloud Result.png', 'Excel Result.xls']
    i=0
    for file in files:
        with open(file, 'rb') as f:
            file_data = f.read()
            file_name = f.name
        msg.add_attachment(file_data, maintype= 'application', subtype= 'octet-stream', filename = names[i])
        i += 1



    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
        
        
