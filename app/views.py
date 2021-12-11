def setup_views(container):
    app = container.app()

    app.add_url_rule('/api/solutions/submit', methods=['POST'], view_func=container.submit_solution.as_view())

    app.add_url_rule('/webhook/copyleaks/completed/<scan_id>', methods=['POST'], view_func=container.completed_webhook.as_view())
    app.add_url_rule('/webhook/copyleaks/error/<scan_id>', methods=['POST'], view_func=container.error_webhook.as_view())
    app.add_url_rule('/webhook/copyleaks/creditsChecked/<scan_id>', methods=['POST'], view_func=container.credits_webhook.as_view())
    app.add_url_rule('/webhook/copyleaks/export/<scan_id>', methods=['POST'], view_func=container.export_webhook.as_view())
