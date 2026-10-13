import os
from flask import Flask, send_from_directory,jsonify
from flask_cors import CORS
from config import Config
from database.db import init_db

# Import Blueprints
from backend.routes.auth import auth_bp
from backend.routes.students import students_bp
from backend.routes.attendance import attendance_bp
from backend.routes.fees import fees_bp
from backend.routes.timetable import timetable_bp
from backend.routes.academic import academic_bp
from backend.routes.algorithms import algorithms_bp

def create_app():
    frontend_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'frontend')
    app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
    app.config.from_object(Config)

    # Enable CORS
    CORS(app, supports_credentials=True)

    # Initialize Database and Seed Data automatically
    with app.app_context():
        init_db()

    # Register API Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(fees_bp)
    app.register_blueprint(timetable_bp)
    app.register_blueprint(academic_bp)
    app.register_blueprint(algorithms_bp)

    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({
            "status": "healthy",
            "service": "CampusDash Smart Campus Management API",
            "version": "1.0.0",
            "database": "SQLite (Initialized)",
            "ads_algorithms_count": 9
        })

    # Frontend Page Routes
    @app.route('/')
    def serve_index():
        return send_from_directory(frontend_dir, 'index.html')

    @app.route('/<path:filename>')
    def serve_static(filename):
        file_path = os.path.join(frontend_dir, filename)
        if os.path.exists(file_path):
            return send_from_directory(frontend_dir, filename)
        # Fallback to index.html for client routing
        return send_from_directory(frontend_dir, 'index.html')

    return app

if __name__ == '__main__':
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    application = create_app()
    port = int(os.environ.get('PORT', 5050))
    print("\n" + "="*55)
    print(">> CampusDash Web Server Started!")
    print(f">> Local URL: http://127.0.0.1:{port}")
    print(">> Demo Credentials:")
    print("   - Admin:   username: admin        | password: admin123")
    print("   - Faculty: username: FAC01        | password: faculty123")
    print("   - Student: username: 25221A0501   | password: Aarav Reddy (or student123)")
    print("="*55 + "\n")
    application.run(host='127.0.0.1', port=port, debug=False)
