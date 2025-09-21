from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_pymongo import PyMongo
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import bcrypt
from bson.objectid import ObjectId
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'nexus-secret-key-change-in-production')
app.config['MONGO_URI'] = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/nexus')

# Initialize MongoDB
mongo = PyMongo(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access NEXUS.'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.email = user_data['email']
        self.created_at = user_data.get('created_at', datetime.utcnow())
        self.streak_count = user_data.get('streak_count', 0)
        self.last_checkin = user_data.get('last_checkin')
        self.badges = user_data.get('badges', [])
        self.total_study_time = user_data.get('total_study_time', 0)
        self.study_groups = user_data.get('study_groups', [])
        self.learning_preferences = user_data.get('learning_preferences', {})

@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        if mongo.db.users.find_one({'$or': [{'username': username}, {'email': email}]}):
            flash('Username or email already exists!', 'error')
            return render_template('register.html')
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        # Create new user
        user_data = {
            'username': username,
            'email': email,
            'password': hashed_password,
            'created_at': datetime.utcnow(),
            'streak_count': 0,
            'last_checkin': None,
            'badges': [],
            'total_study_time': 0,
            'study_groups': [],
            'learning_preferences': {
                'subjects': [],
                'study_time_preference': 'morning',
                'collaboration_level': 'medium'
            }
        }
        
        result = mongo.db.users.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        
        user = User(user_data)
        login_user(user)
        
        flash('Registration successful! Welcome to NEXUS!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user_data = mongo.db.users.find_one({'username': username})
        
        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's current streak and recent activity
    user_data = mongo.db.users.find_one({'_id': ObjectId(current_user.id)})
    
    # Calculate streak status
    today = datetime.utcnow().date()
    streak_status = calculate_streak_status(user_data)
    
    # Get recent check-ins
    recent_checkins = list(mongo.db.checkins.find(
        {'user_id': ObjectId(current_user.id)}
    ).sort('date', -1).limit(7))
    
    # Get weather based on engagement
    weather = get_virtual_weather(user_data)
    
    return render_template('dashboard.html', 
                         user=current_user,
                         streak_status=streak_status,
                         recent_checkins=recent_checkins,
                         weather=weather)

@app.route('/checkin', methods=['POST'])
@login_required
def daily_checkin():
    study_time = int(request.form.get('study_time', 0))
    subjects = request.form.getlist('subjects')
    notes = request.form.get('notes', '')
    
    today = datetime.utcnow().date()
    
    # Check if already checked in today
    existing_checkin = mongo.db.checkins.find_one({
        'user_id': ObjectId(current_user.id),
        'date': today
    })
    
    if existing_checkin:
        flash('You have already checked in today!', 'warning')
        return redirect(url_for('dashboard'))
    
    # Create check-in record
    checkin_data = {
        'user_id': ObjectId(current_user.id),
        'date': today,
        'study_time': study_time,
        'subjects': subjects,
        'notes': notes,
        'timestamp': datetime.utcnow()
    }
    
    mongo.db.checkins.insert_one(checkin_data)
    
    # Update user streak and total study time
    update_user_streak(current_user.id, study_time)
    
    # Check for new badges
    check_and_award_badges(current_user.id)
    
    flash('Daily check-in completed! Keep up the great work!', 'success')
    return redirect(url_for('dashboard'))

def calculate_streak_status(user_data):
    today = datetime.utcnow().date()
    last_checkin = user_data.get('last_checkin')
    
    if not last_checkin:
        return {'current_streak': 0, 'can_checkin': True, 'status': 'Start your streak today!'}
    
    if isinstance(last_checkin, str):
        last_checkin = datetime.fromisoformat(last_checkin).date()
    elif isinstance(last_checkin, datetime):
        last_checkin = last_checkin.date()
    
    days_since_checkin = (today - last_checkin).days
    
    if days_since_checkin == 0:
        return {
            'current_streak': user_data.get('streak_count', 0),
            'can_checkin': False,
            'status': 'Already checked in today!'
        }
    elif days_since_checkin == 1:
        return {
            'current_streak': user_data.get('streak_count', 0),
            'can_checkin': True,
            'status': 'Ready to continue your streak!'
        }
    else:
        return {
            'current_streak': 0,
            'can_checkin': True,
            'status': 'Streak broken. Start fresh today!'
        }

def update_user_streak(user_id, study_time):
    today = datetime.utcnow().date()
    user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    
    last_checkin = user_data.get('last_checkin')
    current_streak = user_data.get('streak_count', 0)
    
    if last_checkin:
        if isinstance(last_checkin, str):
            last_checkin = datetime.fromisoformat(last_checkin).date()
        elif isinstance(last_checkin, datetime):
            last_checkin = last_checkin.date()
        
        days_since = (today - last_checkin).days
        
        if days_since == 1:
            # Continue streak
            new_streak = current_streak + 1
        else:
            # Reset streak
            new_streak = 1
    else:
        # First check-in
        new_streak = 1
    
    # Update user data
    mongo.db.users.update_one(
        {'_id': ObjectId(user_id)},
        {
            '$set': {
                'last_checkin': today,
                'streak_count': new_streak
            },
            '$inc': {
                'total_study_time': study_time
            }
        }
    )

def check_and_award_badges(user_id):
    user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    current_badges = user_data.get('badges', [])
    new_badges = []
    
    # Define badge criteria
    badge_criteria = [
        {'name': 'First Step', 'description': 'Complete your first check-in', 'condition': lambda u: u.get('streak_count', 0) >= 1},
        {'name': 'Week Warrior', 'description': '7-day study streak', 'condition': lambda u: u.get('streak_count', 0) >= 7},
        {'name': 'Month Master', 'description': '30-day study streak', 'condition': lambda u: u.get('streak_count', 0) >= 30},
        {'name': 'Century Scholar', 'description': '100 hours of total study time', 'condition': lambda u: u.get('total_study_time', 0) >= 100},
        {'name': 'Dedication Diamond', 'description': '50-day study streak', 'condition': lambda u: u.get('streak_count', 0) >= 50},
    ]
    
    for badge in badge_criteria:
        if badge['name'] not in current_badges and badge['condition'](user_data):
            new_badges.append(badge['name'])
            
            # Add badge to user
            mongo.db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$push': {'badges': badge['name']}}
            )
            
            # Create badge record
            mongo.db.badge_awards.insert_one({
                'user_id': ObjectId(user_id),
                'badge_name': badge['name'],
                'badge_description': badge['description'],
                'awarded_at': datetime.utcnow()
            })
    
    return new_badges

def get_virtual_weather(user_data):
    streak = user_data.get('streak_count', 0)
    total_time = user_data.get('total_study_time', 0)
    
    # Calculate engagement score
    engagement_score = (streak * 10) + (total_time / 10)
    
    if engagement_score >= 100:
        return {'condition': 'sunny', 'description': 'Brilliant sunshine! Your dedication is lighting up the classroom!'}
    elif engagement_score >= 50:
        return {'condition': 'partly-cloudy', 'description': 'Partly cloudy with rays of success breaking through!'}
    elif engagement_score >= 20:
        return {'condition': 'cloudy', 'description': 'Overcast skies. Time to bring some sunshine with consistent study!'}
    else:
        return {'condition': 'rainy', 'description': 'Stormy weather ahead. Start your learning journey to clear the skies!'}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)