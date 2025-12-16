import os
import requests
from django.conf import settings


class BranchioService:

    @staticmethod
    def create_branch_url(custom_action='invite_member_link', custom_value=1, custom_id=1, extra_data=None, extra_payload=None, request=None):
        default_data = {
            '$desktop_url': getattr(settings, 'BRANCH_DESKTOP_URL', os.getenv('BRANCH_DESKTOP_URL', '')),
            'custom_action': custom_action,
            'custom_id': str(custom_id),
            'custom_value': str(custom_id),
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
            response = requests.post('https://api2.branch.io/v1/url', json=payload, timeout=10)
            response.raise_for_status()
            return response.json().get('url')
        except requests.exceptions.RequestException as e:
            if request is not None:
                try:
                    from libsv1.apps.global_system_log.services import GlobalSystemLogAdd
                    from libsv1.utils.base import BaseUtils
                    GlobalSystemLogAdd(request=request, additional_log={'BranchioService': BaseUtils.log_response_error(locals().get('response'), e)})
                except Exception as e:
                    print(f"BranchioService: {e}")

        return None
