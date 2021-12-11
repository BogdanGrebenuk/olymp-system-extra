from dependency_injector import containers, providers
from dependency_injector.ext import flask as flask_ext
from flask import Flask

from app.api import submit_solution, get_plagiarism_result
from app.services import CodeNormalizer
from app.webhooks import completed_webhook, error_webhook, credits_webhook, export_webhook


class Container(containers.DeclarativeContainer):

    # config

    config = providers.Configuration()

    # app

    app = flask_ext.Application(Flask, __name__)

    # services

    code_normalizer = providers.Factory(
        CodeNormalizer,
        project_root=config.project_root
    )

    # api

    submit_solution = flask_ext.View(
        submit_solution,
        code_normalizer=code_normalizer,
        analysis_url=config.analysis_url,
        cl_email=config.cl_email,
        cl_api_key=config.cl_api_key,
        cl_sandbox=config.cl_sandbox
    )

    get_plagiarism_results = flask_ext.View(
        get_plagiarism_result,
        project_root=config.project_root
    )

    # webhooks

    completed_webhook = flask_ext.View(
        completed_webhook,
        cl_email=config.cl_email,
        cl_api_key=config.cl_api_key,
        project_root=config.project_root
    )

    error_webhook = flask_ext.View(
        error_webhook
    )

    credits_webhook = flask_ext.View(
        credits_webhook
    )

    export_webhook = flask_ext.View(
        export_webhook
    )
