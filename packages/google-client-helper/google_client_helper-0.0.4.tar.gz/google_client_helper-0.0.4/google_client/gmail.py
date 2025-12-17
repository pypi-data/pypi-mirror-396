import email
import base64
import dateutil.parser
from bs4 import BeautifulSoup
from .service import GoogleServiceMixin


class GmailEmail:

    def __init__(self, gmail, email_id):
        self.email_id = email_id
        self.gmail = gmail
        self.html_part = []
        self.text_part = []
        self.email = self.get_email()
        self.headers = self.get_headers()
        self.find_html_parts(self.email['payload'])

    @property
    def date(self):
        return dateutil.parser.parse(self.headers['Date'])

    def get_headers(self):
        return {h['name']: h['value'] for h in self.email['payload']['headers']}

    def get_email(self):
        return self.gmail.service.users().messages().get(userId=self.gmail.account_email,
                                                         id=self.email_id, format='full').execute()

    def find_html_parts(self, part):
        if part['mimeType'] == 'text/html':
            try:
                self.html_part.append(base64.urlsafe_b64decode(part['body']['data']).decode('utf-8'))
            except KeyError:
                pass
        if part['mimeType'] == 'text/plain':
            self.text_part.append(base64.urlsafe_b64decode(part['body']['data']).decode('utf-8'))
        if part.get('parts'):
            for p in part['parts']:
                self.find_html_parts(p)

    def content(self):
        content = 'NONE'
        if len(self.html_part) > 0:
            soup = BeautifulSoup(self.html_part[0], 'html.parser')
            content = soup.get_text('\n')
        elif len(self.text_part) > 0:
            content = self.text_part[0]
        return content


class Gmail(GoogleServiceMixin):

    api_name = 'gmail'
    api_version = 'v1'
    scopes = ['https://www.googleapis.com/auth/gmail.readonly']

    def __init__(self, credentials, account_email):
        super().__init__(credentials, account_email)
        self.emails = []
        self.email_contents = []

    def get_emails(self, query, max_results=20):
        emails = self.service.users().messages().list(userId=self.account_email, q=query,
                                                      maxResults=max_results).execute().get('messages', [])
        for e in emails:
            self.emails.append(GmailEmail(self, e['id']))
        return self

    def get_email(self, gmail_id):
        self.emails.append(GmailEmail(self, gmail_id))

    def get_mime_message(self, msg_id):
        message = self.service.users().messages().get(userId=self.account_email, id=msg_id, format='raw').execute()
        msg_str = str(base64.urlsafe_b64decode(message['raw'].encode('ASCII')))
        mime_msg = email.message_from_string(msg_str)
        return mime_msg

    def get_email_contents(self, extra_slug=''):
        for e in self.emails:
            self.email_contents.append(
                {'id': (f'gmailid-{e.email_id}-account-{self.account_email[:self.account_email.find("@")]}'
                        f'-new-email{extra_slug}'),
                 'Date': dateutil.parser.parse(e.headers['Date']),
                 'From': e.headers['From'],
                 'To': e.headers['To'],
                 'content': e.content().replace('\n', '<br>'),
                 }
            )
        return self
