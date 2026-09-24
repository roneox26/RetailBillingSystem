from flask import jsonify, render_template, request

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith('/api/'):
            return jsonify({'status': 'error', 'message': 'Resource not found'}), 404
        return render_template('index.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
        return render_template('index.html'), 500
