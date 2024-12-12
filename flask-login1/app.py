from flask import Flask
from extensions import db, bcrypt, login_manager
from models import User
from routes import init_routes


# Initialize App
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secretkey'

# Initialize Extensions
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)

# User Loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register Routes
init_routes(app)

# Database Initialization
with app.app_context():
    db.create_all()

# Run Server
if __name__ == "__main__":
    app.run(debug=True)
