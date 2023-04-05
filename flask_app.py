import csv
import smtplib
import os
from email.message import EmailMessage
from flask import Flask, render_template, request
from twilio.rest import Client
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pathlib import Path

# Hi there and welcome. This app is rather simple, but if you fill the form in contact section, the website will send
# me a text and an email, and it will send you a text and an email with PDF containing your message. It demonstrates my
# ability to work with APIs and some basic python functionalities. Section #1 is devoted to website basic
# functionalities. Section #2 is devoted to sending emails, SMSs and creating PDF. The FE was created by
# www.mashup-template.com. || Dont forget to add your own name, gmail (+another email), tel and Twilio keys and number,
# use ctrl + f and seek for 'ADD_YOUR_OWN_DATA!' in this code ||

# #1st section

app = Flask(__name__)

global_tel = ""
global_email = ""
global_message = ""

@app.route("/")
def landing():
    return render_template('./index.html')


# general route for all templates
@app.route("/<string:page_name>")
def html_page(page_name):
    return render_template(page_name)


# handles the input data and writes to txt file || .txt database || unused
# def write_to_file(data):
#     with open('database.txt', mode='a') as database:
#         email = data['email']
#         subject = data['subject']
#         message = data['message']
#         file = database.write(f'\n{email}, {subject}, {message}')


# handles the input data and writes to csv file || .csv database
def write_to_csv(data):
    with open('database.csv', mode='a', newline='') as database2:
        global global_tel
        global global_email
        global global_message
        global_tel = data['tel']
        global_email = data['email']
        subject = data['subject']
        global_message = data['message']
        csv_writer = csv.writer(database2, delimiter=',', quotechar=';', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([global_tel, global_email, subject, global_message])
        print(global_email, global_tel)


# cashes the form data, stores them as dict, redirects to thankyou.html, calls pdf, email, SMS functions
@app.route('/submit_form', methods=['POST', 'GET'])
def submit_form():
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            write_to_csv(data)
            create_PDF(data)
            send_me_email()
            send_me_sms()
            # send_guy_sms() # This only works if the number is added to white-list on Twilio, or with paid Twilio acc
            send_guy_email()
            return render_template('thankyou.html')
        except:
            return 'did not save data to csv'
    else:
        return 'something went wrong'


# #2nd section
# sends an email to me
def send_me_email():
    email = EmailMessage()
    email['from'] = 'ADD_YOUR_OWN_DATA!'
    email['to'] = 'ADD_YOUR_OWN_DATA!'
    email['subject'] = 'ADD_YOUR_OWN_DATA!'
    email.set_content(f'Hey my other me, someone sent you an email. Dont hesitate and reply ASAP!!!\nEmail: {email}\nMessage: {global_message}')

    with smtplib.SMTP(host='smtp.gmail.com', port=587) as server:
        server.ehlo()
        server.starttls()
        server.login('ADD_YOUR_OWN_DATA!', 'ADD_YOUR_OWN_DATA!')
        server.send_message(email)


# sends confirmation email to guy, attaches PDF from create_PDF func, deletes the PDF in the end
def send_guy_email():
    email = EmailMessage()
    email['from'] = 'ADD_YOUR_OWN_DATA!'
    email['to'] = global_email
    email['subject'] = 'Thank you for your email!'
    email.set_content('Hi there. I wanted to thank you for contacting me. I will reply ASAP. Best regards, NAME')

    pdf_path = Path("output.pdf")
    with pdf_path.open("rb") as f:
        pdf_data = f.read()
    email.add_attachment(pdf_data, maintype='application', subtype='pdf', filename=str(pdf_path))

    with smtplib.SMTP(host='smtp.gmail.com', port=587) as server:
        server.ehlo()
        server.starttls()
        server.login('ADD_YOUR_OWN_DATA!', 'ADD_YOUR_OWN_DATA!')
        server.send_message(email)

    os.remove("output.pdf")


# sends a SMS with the use of Twilio API to my phone number
def send_me_sms():
    account_sid = "ADD_YOUR_OWN_DATA!"
    auth_token = "ADD_YOUR_OWN_DATA!"
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body="Someone just sent you an email broh",
        from_="+ADD_YOUR_OWN_DATA!",
        to="+420_ADD_YOUR_OWN_DATA!"
    )

    print(message.sid)


# sends a SMS with the use of Twilio API to guy phone number || The problem here is that Twilio trial acc only allow
# the SMSs sending to pre-authorized numbers. Either pay for a normal acc, or leave this func deactivated (line 70)
def send_guy_sms():
    account_sid = "ADD_YOUR_OWN_DATA!"
    auth_token = "ADD_YOUR_OWN_DATA!"
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body = "Hey! I wanted to thank you for reaching out. I will check the email soon. Until then, take care. NAME",
        from_="+ADD_YOUR_OWN_DATA!",
        to = global_tel
    )

    print(message.sid)


# creates a PDF with the input information - email, subject, message
def create_PDF(data):
    try:
        c = canvas.Canvas("output.pdf", pagesize=letter)
        c.setFont("Helvetica", 14)
        c.drawString(72, 720, f"Email: {data['email']}")
        c.drawString(72, 680, f"Subject: {data['subject']}")
        c.drawString(72, 640, f"Message: {data['message']}")
    finally:
        c.save()
