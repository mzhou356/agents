from __future__ import annotations

from typing import Dict

from agents import Agent
from agents import function_tool
from research_chat import gemini_model


@function_tool
def send_email(subject: str, html_body: str) -> Dict[str, str]:
    """ Send an email with the given subject and HTML body """
    # sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    # from_email = Email("ed@edwarddonner.com") # put your verified sender here
    # to_email = To("ed.donner@gmail.com") # put your recipient here
    # content = Content("text/html", html_body)
    # mail = Mail(from_email, to_email, subject, content).get()
    # response = sg.client.mail.send.post(request_body=mail)
    # print("Email response", response.status_code)
    print(f"subject: {subject}")
    print(f"body: {html_body} ")
    return {'status': 'success'}


INSTRUCTIONS = """You are able to send a nicely formatted HTML email based on a detailed report.
You will be provided with a detailed report. You should use your tool to send one email, providing the
report converted into clean, well presented HTML with an appropriate subject line."""

email_agent = Agent(
    name='Email agent',
    instructions=INSTRUCTIONS,
    tools=[send_email],
    model=gemini_model,
)
