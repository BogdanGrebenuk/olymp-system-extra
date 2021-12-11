import requests

from copyleaks.copyleaks import Copyleaks


def completed_webhook(scan_id, cl_email, cl_api_key, project_root):
    auth_token = Copyleaks.login(cl_email, cl_api_key)
    headers = {
        'Authorization': f'Bearer {auth_token["access_token"]}'
    }
    response = requests.get(
        f'https://api.copyleaks.com/v3/downloads/{scan_id}/report.pdf',
        headers=headers)

    with open(f'{project_root}/results/result_{scan_id}.pdf', 'wb') as file:
        file.write(response.content)
    return 'Result from completed webhook'


def error_webhook(scan_id):
    print(f'Error webhook triggered, scan_id: {scan_id}')
    return 'Result from error webhook'


def credits_webhook(scan_id):
    print(f'Credits webhook triggered, scan_id: {scan_id}')
    return 'Result from credits webhook'


def export_webhook(scan_id):
    return 'Result from export webhook'
