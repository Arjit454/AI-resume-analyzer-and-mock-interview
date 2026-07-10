import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # sqlite needs this folder to exist before it can create the db file —
    # it doesn't always survive zipping/git since it starts out empty
    os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    from models.user import User
    from models.resume import Resume
    from models.interview import InterviewSession, InterviewAnswer
    from models.roadmap import LearningRoadmap
    from models.activity import ActivityLog

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.errorhandler(413)
    def file_too_large(e):
        if request.path.startswith("/upload"):
            return jsonify(success=False, error="File is too large. Max size is 5MB."), 413
        return "File is too large.", 413

    # blueprints get registered here as we build them out
    from routes.main_routes import main_bp
    from routes.auth_routes import auth_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.resume_routes import resume_bp
    from routes.career_routes import career_bp
    from routes.interview_routes import interview_bp
    from routes.report_routes import report_bp
    from routes.learning_routes import learning_bp
    from routes.profile_routes import profile_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(career_bp)
    app.register_blueprint(interview_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(learning_bp)
    app.register_blueprint(profile_bp)

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
