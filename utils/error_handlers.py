from flask import jsonify, render_template

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        if '/api/' in request.path:
            return jsonify({'status': 'error', 'message': 'Resource not found'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        if '/api/' in request.path:
            return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500
