# 💼 Budget Tracker with Authentication

A secure, user-friendly budget tracking application built with Streamlit that includes email verification and user authentication.

## 🚀 Features

### 🔐 Authentication System
- **User Registration** with email verification
- **Secure Login** with password hashing
- **Email Verification** with 6-digit codes
- **Session Management** with automatic logout
- **User Data Isolation** - each user sees only their own data

### 📊 Budget Management
- **Income Tracking** - record all income sources
- **Expense Categorization** - organize expenses by type
- **Savings & Investments** - track savings and investment contributions
- **Visual Analytics** - charts and graphs for insights
- **Monthly Reports** - comprehensive financial analysis
- **Data Export** - download your data in CSV format

### 🎨 User Experience
- **Modern UI** with gradient backgrounds and smooth animations
- **Responsive Design** that works on all devices
- **Intuitive Navigation** with clear tabs and sections
- **Real-time Validation** and helpful error messages
- **Financial Health Score** with personalized recommendations

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd monthly_budget_tracker
   ```

2. **Install dependencies:**
   ```bash
   pip install streamlit pandas altair
   ```

3. **Configure email settings (optional):**
   - Edit `config.py` with your Gmail credentials
   - Or use development mode (codes shown on screen)

4. **Run the application:**
   ```bash
   streamlit run main.py
   ```

## 📧 Email Configuration

### Development Mode (Default)
The app runs in development mode by default, showing verification codes on screen instead of sending emails.

### Production Mode
To enable actual email sending:

1. **Edit `config.py`:**
   ```python
   SENDER_EMAIL = "your-email@gmail.com"
   SENDER_PASSWORD = "your-gmail-app-password"
   DEVELOPMENT_MODE = False
   ```

2. **Gmail Setup:**
   - Enable 2-factor authentication on your Gmail account
   - Generate an "App Password" (Google Account → Security → App Passwords)
   - Use the app password (not your regular password)

3. **Restart the app** after making changes

## 🔐 How Authentication Works

### Registration Process
1. **Enter Details** - Email, name, and password
2. **Email Verification** - Receive 6-digit code (shown on screen in dev mode)
3. **Code Verification** - Enter the code to verify email
4. **Password Setup** - Create final password
5. **Account Created** - Ready to login

### Login Process
1. **Enter Credentials** - Email and password
2. **Authentication** - Secure password verification
3. **Access Granted** - Full access to budget features

### Security Features
- **Password Hashing** - SHA-256 encryption
- **Session Management** - Automatic logout on browser close
- **Data Isolation** - Users can only access their own data
- **Email Verification** - Prevents fake accounts
- **Code Expiration** - Verification codes expire in 10 minutes

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    user_name TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    is_verified BOOLEAN DEFAULT 0
);
```

### Verification Codes Table
```sql
CREATE TABLE verification_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    code TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    expires_at TEXT NOT NULL,
    is_used BOOLEAN DEFAULT 0
);
```

### Budget Table
```sql
CREATE TABLE budget (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT,
    month TEXT,
    year INTEGER,
    category TEXT,
    sub_category TEXT,
    type TEXT,
    amount REAL,
    created_at TEXT DEFAULT (datetime('now'))
);
```

## 🎯 Usage Guide

### Getting Started
1. **Register** - Create a new account with email verification
2. **Login** - Access your secure budget dashboard
3. **Add Entries** - Start tracking your income, expenses, and savings
4. **View Analytics** - Check your financial health and trends
5. **Export Data** - Download your budget data for backup

### Budget Categories
- **Essential Expenses** - Rent, utilities, groceries, medical
- **EMIs** - Home loan, car loan, personal loans
- **Lifestyle Expenses** - Shopping, travel, entertainment
- **Savings & Investments** - Mutual funds, stocks, emergency fund

### Features by Tab
- **Add Entry** - Input income, expenses, and savings
- **Dashboard** - Overview with charts and financial health score
- **Reports** - Historical analysis and trends
- **History** - Edit and manage past entries

## 🔧 Configuration Options

### Email Settings (`config.py`)
```python
SENDER_EMAIL = "your-email@gmail.com"
SENDER_PASSWORD = "your-app-password"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
VERIFICATION_CODE_EXPIRY = 600  # 10 minutes
CODE_LENGTH = 6
DEVELOPMENT_MODE = True  # Set to False for production
```

### Customization
- **Categories** - Modify expense categories in the global variables
- **Styling** - Update CSS in the main.py file
- **Features** - Add new functionality by extending the existing structure

## 🚨 Security Notes

- **Never commit** your `config.py` with real credentials
- **Use environment variables** for production deployments
- **Regular backups** of your database file
- **Strong passwords** recommended for user accounts
- **HTTPS** recommended for production use

## 🐛 Troubleshooting

### Common Issues
1. **Email not sending** - Check Gmail app password and 2FA settings
2. **Database errors** - Ensure write permissions in the app directory
3. **Import errors** - Install all required dependencies
4. **Session issues** - Clear browser cache and restart app

### Development Tips
- Use development mode for testing
- Check the browser console for errors
- Monitor the Streamlit logs for debugging
- Test with different email addresses

## 📈 Future Enhancements

- **Password Reset** functionality
- **Two-Factor Authentication** (2FA)
- **Data Backup** and restore features
- **Budget Goals** and alerts
- **Mobile App** version
- **Multi-currency** support
- **Bill Reminders** and notifications

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

---

**Happy Budgeting! 💰** 