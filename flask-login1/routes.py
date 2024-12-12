import os
import secrets
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from models import User
from werkzeug.utils import secure_filename  
from extensions import db, bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import InputRequired, Length, ValidationError


# Configure file upload folder
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Configure file uploading
# No need for 'app' reference here, as it will be passed from app.py
def init_routes(app):
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    class SignupForm(FlaskForm):
        username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
        password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
        name = StringField(validators=[InputRequired()], render_kw={"placeholder": "Full Name"})
        age = StringField(validators=[InputRequired()], render_kw={"placeholder": "Age"})
        gender = StringField(validators=[InputRequired()], render_kw={"placeholder": "Gender"})
        dob = StringField(validators=[InputRequired()], render_kw={"placeholder": "Date of Birth (YYYY-MM-DD)"})
        profile_picture = FileField("Profile Picture")  # This MUST be here
        submit = SubmitField("Signup")

        def validate_username(self, username):
            if User.query.filter_by(username=username.data).first():
                raise ValidationError('This username already exists. Please choose a different one.')

        def save_picture(self, picture_data):
            random_hex = secrets.token_hex(8)
            _, f_ext = os.path.splitext(picture_data.filename)
            picture_fn = random_hex + f_ext
            picture_path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], picture_fn)
            picture_data.save(picture_path)
            return picture_fn

    class LoginForm(FlaskForm):
        username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
        password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
        submit = SubmitField("Login")

    # Routes
    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        form = SignupForm()
        if form.validate_on_submit():
            if form.profile_picture.data:
                file = form.profile_picture.data
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            new_user = User(
                username=form.username.data,
                password=hashed_password,
                name=form.name.data,
                age=int(form.age.data),
                gender=form.gender.data,
                dob=form.dob.data,
                profile_picture=filename  # Save the filename in the database
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))

        return render_template('signup.html', form=form)


    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('profile'))
            flash("Login failed. Please check your username and password.", "danger")
        return render_template('login.html', form=form)

    @app.route('/profile')
    @login_required
    def profile():
        return render_template('profile.html', user=current_user)

    @app.route('/logout', methods=['GET'])
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))  # Correct endpoint name

