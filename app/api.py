import base64
import uuid

from copyleaks.copyleaks import Copyleaks, Products
from copyleaks.exceptions.command_error import CommandError
from copyleaks.models.submit.document import FileDocument
from copyleaks.models.submit.properties.scan_properties import ScanProperties
from flask import request, jsonify


def submit_solution(
        code_normalizer,
        analysis_url,
        cl_email,
        cl_api_key,
        cl_sandbox
        ):
    body = request.json
    code = body.get('code')
    solution_id = str(uuid.uuid4())

    if code is None:
        return jsonify({
            'message': '\'code\' field is missing.',
            'payload': {}
        }), 400

    normalized_code = code_normalizer.normalize(code, solution_id)
    encoded_file_content = base64.b64encode(normalized_code.encode('utf-8')).decode('utf8')
    filename = f'solution_{solution_id}.py'

    auth_token = Copyleaks.login(cl_email, cl_api_key)

    file_submission = FileDocument(encoded_file_content, filename)

    scan_properties = ScanProperties(analysis_url + '/webhook/copyleaks/{STATUS}/' + solution_id)
    if bool(int(cl_sandbox)):
        scan_properties.set_sandbox(bool(int(cl_sandbox)))
    scan_properties.set_pdf({'create': True, 'title': 'Olymp System powered by KNKG'})
    file_submission.set_properties(scan_properties)
    try:
        Copyleaks.submit_file(Products.EDUCATION, auth_token, solution_id, file_submission)
        return jsonify({
            'message': 'Solution has been successfully submitted for plagiarism check.',
            'payload': {'solutionId': solution_id}
        }), 200
    except CommandError as ce:
        response = ce.get_response()
        print(response.content)
        return jsonify({
            'message': response.content,
            'payload': {}
        }), 500


def get_plagiarism_result(scan_id, project_root):
    try:
        with open(project_root + f'/results/result_{scan_id}.pdf', 'rb') as file:
            content = file.read()
    except Exception:
        return jsonify({
            'message': 'Result is not ready',
            'payload': {'content': None}
        }), 200
    base64_encoded_content = base64.b64encode(content)
    base64_content = base64_encoded_content.decode('utf-8')
    return jsonify({
        'message': 'Result is ready',
        'payload': {'content': base64_content}
    })


def get_management_analysis(management_analyzer, project_root):
    body = request.json
    request_id = str(uuid.uuid4())
    be_git_info = body.get('BEGitInfo')
    fe_git_info = body.get('FEGitInfo')
    file_path = f'{project_root}/plots/plot_{request_id}.png'

    management_analyzer.create_plot(file_path, be_git_info, fe_git_info, '2021-11-27', '2021-11-28')

    with open(file_path, 'rb') as file:
        content = file.read()
    base64_encoded_content = base64.b64encode(content)
    base64_content = base64_encoded_content.decode('utf-8')

    return jsonify({
        'message': 'Analysis is ready',
        'payload': {'content': base64_content}
    })
