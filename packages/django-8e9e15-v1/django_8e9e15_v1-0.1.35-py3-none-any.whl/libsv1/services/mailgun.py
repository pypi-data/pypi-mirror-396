import requests
from django.conf import settings
from django.template.loader import render_to_string

#MailgunService.send(email='bearablyk@gmail.com', subject='test', template_view='emails/test-email.html', template_context={'name': 'User Name'}, request=request)

class MailgunService:

    @staticmethod
    def send(email, subject, template_view, template_context, from_email=None, request=None):
        html_content = render_to_string(template_view, template_context)

        api_url = f"https://{settings.MAILGUN_ENDPOINT}/v3/{settings.MAILGUN_DOMAIN}/messages"
        auth = ("api", settings.MAILGUN_SECRET)
        if not from_email:
            from_email = f"{settings.PROJECT_NAME} <noreply@{settings.MAILGUN_DOMAIN}>"

        email_data = {
            "from": from_email,
            "to": [email],
            "subject": subject,
            "html": html_content,
        }
        response = requests.post(api_url, auth=auth, data=email_data)
        print(response)
        if request:
            if response.status_code != 200:
                try:
                    data = response.json()
                except Exception:
                    data = response.text

                try:
                    from libsv1.apps.global_system_log.services import GlobalSystemLogAdd
                    GlobalSystemLogAdd(request=request, additional_log={'mailgun': data})
                except Exception as e:
                    print(f"MailgunService: {e}")

