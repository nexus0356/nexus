# NEXUS - Intelligent Student Engagement Platform

NEXUS is an innovative learning platform that combines gamification, habit-building, and social intelligence to create a deeply rewarding educational ecosystem. Built with Flask and MongoDB, NEXUS motivates students through achievement-based progression and personalized collaboration.

## 🌟 Key Features

### 📚 Core Learning Features
- **Daily Study Streaks**: Track daily learning activities to build consistent study habits
- **Smart Check-ins**: Record study time, subjects, and personal notes
- **Achievement Badges**: Unlock digital badges for reaching learning milestones
- **Personalized Dashboard**: Visual progress tracking with real-time statistics

### 🎮 Gamification Elements
- **Virtual Weather System**: Dynamic classroom environment that reflects engagement levels
- **Streak Mechanics**: Scientifically-proven habit formation through daily consistency
- **Badge Collection**: Permanent achievements stored in user profiles
- **Legacy Building**: Create digital markers for major milestones (Coming Soon)

### 👥 Social Features
- **Intelligent Study Groups**: AI-powered matching based on interests and learning patterns (Coming Soon)
- **Collaborative Learning**: Connect with peers for accountability and growth (Coming Soon)
- **Community Impact**: Share achievements and inspire other learners (Coming Soon)

## 🛠️ Tech Stack

- **Backend**: Python Flask
- **Database**: MongoDB with PyMongo
- **Authentication**: Flask-Login with secure password hashing
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Icons**: Font Awesome
- **Fonts**: Google Fonts (Inter)

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- MongoDB (local installation or MongoDB Atlas)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd NEXUS
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv nexus_env
   
   # On Windows
   nexus_env\Scripts\activate
   
   # On macOS/Linux
   source nexus_env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your configuration
   # MONGODB_URI=mongodb://localhost:27017/nexus
   # SECRET_KEY=your-secret-key-here
   ```

5. **Start MongoDB**
   - For local MongoDB: Ensure MongoDB service is running
   - For MongoDB Atlas: Update MONGODB_URI in .env with your connection string

6. **Run the application**
   ```bash
   python main.py
   ```

7. **Access NEXUS**
   Open your browser and navigate to `http://localhost:5000`

## 📊 Database Schema

### Users Collection
```javascript
{
  _id: ObjectId,
  username: String,
  email: String,
  password: String (hashed),
  created_at: DateTime,
  streak_count: Number,
  last_checkin: Date,
  badges: [String],
  total_study_time: Number,
  study_groups: [ObjectId],
  learning_preferences: {
    subjects: [String],
    study_time_preference: String,
    collaboration_level: String
  }
}
```

### Check-ins Collection
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  date: Date,
  study_time: Number,
  subjects: [String],
  notes: String,
  timestamp: DateTime
}
```

### Badge Awards Collection
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  badge_name: String,
  badge_description: String,
  awarded_at: DateTime
}
```

## 🏆 Badge System

NEXUS includes a comprehensive badge system to recognize learning achievements:

- **First Step**: Complete your first check-in
- **Week Warrior**: Maintain a 7-day study streak
- **Month Master**: Achieve a 30-day study streak
- **Century Scholar**: Accumulate 100 hours of total study time
- **Dedication Diamond**: Reach a 50-day study streak

## 🌤️ Virtual Weather System

The virtual weather system provides ambient feedback based on user engagement:

- **☀️ Sunny**: High engagement (100+ engagement points)
- **⛅ Partly Cloudy**: Good engagement (50-99 points)
- **☁️ Cloudy**: Moderate engagement (20-49 points)
- **🌧️ Rainy**: Low engagement (0-19 points)

*Engagement Score = (Streak Count × 10) + (Total Study Time ÷ 10)*

## 🔧 Configuration

### Environment Variables
- `MONGODB_URI`: MongoDB connection string
- `SECRET_KEY`: Flask secret key for session management
- `FLASK_ENV`: Environment mode (development/production)
- `FLASK_DEBUG`: Enable/disable debug mode

### Customization
- Modify badge criteria in `check_and_award_badges()` function
- Adjust weather thresholds in `get_virtual_weather()` function
- Update UI themes in `templates/base.html` CSS variables

## 🚧 Upcoming Features

- **Study Group Matching**: AI-powered peer connections
- **Advanced Analytics**: Learning pattern insights and recommendations
- **Legacy Building**: Permanent milestone markers in shared virtual space
- **Mobile App**: Native iOS and Android applications
- **Integration APIs**: Connect with popular learning management systems

## 🤝 Contributing

We welcome contributions to NEXUS! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ for the learning community
- Inspired by habit-formation research and gamification principles
- Special thanks to all beta testers and early adopters

## 📞 Support

For support, questions, or feature requests:
- Create an issue on GitHub
- Email: support@nexus-platform.com
- Documentation: [Wiki](https://github.com/your-repo/nexus/wiki)

---

**Start your intelligent learning journey with NEXUS today!** 🚀
