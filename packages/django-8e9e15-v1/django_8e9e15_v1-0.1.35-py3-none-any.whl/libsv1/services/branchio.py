import json
import os
import re
import requests
from django.conf import settings


class BranchioService:

    @staticmethod
    def create_branch_url(custom_action='invite_member_link', custom_id=1, extra_data=None, extra_payload=None, request=None):
        url = 'https://api2.branch.io/v1/url'

        default_data = {
            '$desktop_url': getattr(settings, 'BRANCH_DESKTOP_URL', os.getenv('BRANCH_DESKTOP_URL', '')),
            'custom_action': custom_action,
            'custom_id': str(custom_id),
        }

        if extra_data:
            default_data.update(extra_data)

        payload = {
            "branch_key": getattr(settings, 'BRANCH_API_KEY', os.getenv('BRANCH_API_KEY', '')),
            "data": default_data
        }

        if extra_payload:
            payload.update(extra_payload)

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json().get('url')

        except requests.exceptions.RequestException as e:
            try:
                from libsv1.apps.global_system_log.services import GlobalSystemLogAdd
                # from libsv1.utils import base
                # log = log_response_error()
                GlobalSystemLogAdd(request=request, additional_log={'branchio': []})
            except Exception as e:
                print(f"MailgunService: {e}")


            print(f"Branch.io Error: {e}")
            if e.response:
                print(f"Response body: {e.response.text}")
            return None
