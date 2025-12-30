@echo off
echo ============================================
echo  HEALTH & AI ASSISTANT - BACKEND SETUP
echo ============================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install core dependencies
echo 📚 Installing Flask and core dependencies...
pip install flask flask-cors python-dotenv pyjwt

REM Install database dependencies
echo 💾 Installing database packages...
pip install flask-sqlalchemy flask-migrate

REM Install optional dependencies (comment out if not needed)
echo 📊 Installing additional utilities...
pip install flask-limiter  # For rate limiting
pip install python-dateutil  # For date handling

REM Create required directories
echo 📁 Creating directories...
if not exist uploads mkdir uploads
if not exist logs mkdir logs
if not exist migrations mkdir migrations

REM Generate requirements.txt
echo 📝 Generating requirements.txt...
pip freeze > requirements.txt

echo.
echo ============================================
echo ✅ SETUP COMPLETE!
echo ============================================
echo.
echo 📋 Next steps:
echo 1. Edit .env file with your configuration
echo 2. Activate environment: venv\Scripts\activate
echo 3. Initialize database: 
echo    - python app.py (first run will create tables)
echo 4. Run the server: python app.py
echo.
echo ⚙️  Default credentials:
echo    Email: demo@example.com
echo    Password: demo123
echo.
echo 🌐 API will run at: http://localhost:5000
echo 🌐 Frontend should be at: http://localhost:3000
echo.
pause