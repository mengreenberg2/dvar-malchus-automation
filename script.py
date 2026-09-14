import os
import re
import smtplib
from email.message import EmailMessage
import requests
from bs4 import BeautifulSoup

SITE_URL = "https://dvarmalchus.org/"
RECIPIENT_EMAIL = "mengreenberg1@gmail.com"
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")

def get_latest_dvar_malchus_url():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(SITE_URL, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.endswith(".pdf"):
            if not href.startswith("http"):
                href = requests.compat.urljoin(SITE_URL, href)
            return href
            
    pdf_match = re.search(r'https?://[^\s"]+\.pdf', response.text)
    if pdf_match:
        return pdf_match.group(0)
        
    return None

def send_email(pdf_url):
    pdf_response = requests.get(pdf_url)
    pdf_response.raise_for_status()
    pdf_data = pdf_response.content
    filename = pdf_url.split("/")[-1]

    msg = EmailMessage()
    msg["Subject"] = "Weekly Dvar Malchus"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL
    msg.set_content(
        f"Good week!\n\nAttached is the weekly Dvar Malchus.\nDirect Link: {pdf_url}"
    )

    msg.add_attachment(
        pdf_data,
        maintype="application",
        subtype="pdf",
        filename=filename
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
        smtp.send_message(msg)
    print("Email sent successfully!")

if __name__ == "__main__":
    url = get_latest_dvar_malchus_url()
    if url:
        print(f"Found PDF: {url}")
        send_email(url)
    else:
        print("No PDF link found on the site.")
