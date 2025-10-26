# Phoenix CRM Application

A modern CRM application built with FastAPI backend, Supabase database, GPT4All AI integration, and PyQt6 GUI.

## Prerequisites

- Python 3.11 or higher
- Git
- Virtual environment (recommended)

## Quick Start

### 1. Setup Environment

```bash
# Clone or navigate to the project directory
cd /Users/jordaneaster/Metro_Minds/phx-python/phoenix_crm

# Check your Python installation
python3 --version  # Should show Python 3.11+

# Use the fixed setup script for macOS
chmod +x setup_fixed.sh
./setup_fixed.sh
```

### 2. Run the Application

#### Option A: Run with Fixed Scripts (Recommended for macOS)
```bash
# Run the full application
./run_app_fixed.sh
```

#### Option B: Run with Original Scripts
```bash
# Make scripts executable
chmod +x setup.sh run_backend.sh run_gui.sh run_app.sh

# Run the setup first
./setup.sh

# Run the full application
./run_app.sh
```

#### Option C: Run Manually

**Terminal 1 - Backend:**
```bash
source venv/bin/activate
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - GUI:**
```bash
source venv/bin/activate
cd gui
python main.py
```

## Project Structure

```
phoenix_crm/
├── backend/               # FastAPI backend
│   ├── main.py           # Main application entry
│   ├── api/              # API endpoints
│   ├── services/         # External service clients
│   └── requirements.txt  # Backend dependencies
├── gui/                  # PyQt6 GUI application
│   ├── main.py          # GUI entry point
│   ├── login_window.py  # Login interface
│   ├── dashboard_window.py # Main dashboard
│   └── requirements.txt # GUI dependencies
├── .env                 # Environment variables
└── docker-compose.yml   # Docker setup (optional)
```

## Features

- **Authentication**: Secure login with Supabase Auth
- **Lead Management**: Create, view, and manage leads
- **AI Assistant**: GPT4All integration for intelligent suggestions
- **Modern GUI**: Professional PyQt6 interface
- **Real-time Updates**: Threaded API calls for smooth UX

## Troubleshooting

### Common Issues

1. **"python: command not found"**
   ```bash
   # On macOS, use python3
   python3 --version
   # If not installed, install via Homebrew:
   brew install python3
   ```

2. **"ModuleNotFoundError: No module named 'jwt'"**
   - This is fixed in the updated auth.py file
   - The correct import is `from jose import jwt` not `import jwt`

3. **PyQt6 Symbol Error on macOS (dlopen QtCore.abi3.so)**
   ```bash
   # This is a known PyQt6 macOS compatibility issue
   # Solution: Use Tkinter instead or fix PyQt6 installation
   
   # Option 1: Reinstall PyQt6 with specific version
   source venv/bin/activate
   pip uninstall PyQt6 PyQt6-Qt6 PyQt6-sip
   pip install --upgrade pip
   pip install PyQt6==6.5.3
   
   # Option 2: If still failing, install via Homebrew
   brew install pyqt6
   pip install --no-deps PyQt6
   
   # Option 3: Use system Python with PyQt6
   brew install python-pyqt6
   # Then use system python3 instead of venv
   
   # Option 4: Switch to Tkinter GUI (see Alternative GUI section)
   ```

4. **"Cannot connect to server"**
   - Make sure the backend is running on port 8000
   - Check firewall settings

5. **"Module not found" errors**
   - Ensure virtual environment is activated: `source venv/bin/activate`
   - Reinstall requirements: `pip install -r requirements.txt`

6. **PyQt6 general installation issues on macOS**
   ```bash
   # Install system dependencies
   brew install python-tk
   pip install --upgrade pip
   pip install PyQt6
   
   # If still having issues, try:
   pip uninstall PyQt6
   pip install --no-cache-dir PyQt6
   ```

7. **Supabase connection issues**
   - Verify your Supabase URL and key in `.env`
   - Check Supabase project status

8. **Virtual environment activation fails**
   ```bash
   # Make sure you're in the project directory
   cd /Users/jordaneaster/Metro_Minds/phx-python/phoenix_crm
   # Create fresh virtual environment
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   ```

### Alternative GUI (Tkinter) - If PyQt6 Issues Persist

If PyQt6 continues to have issues on your system, you can use the Tkinter version:

```bash
# Create Tkinter version of GUI files
./create_tkinter_gui.sh

# Run with Tkinter GUI instead
cd gui
python main_tkinter.py
```

### Development Mode

For development with auto-reload:

```bash
# Activate virtual environment first
source venv/bin/activate

# Backend with auto-reload
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# GUI (restart manually when needed)
cd gui
python main.py
```

### Manual Installation (if scripts fail)

```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install backend dependencies
cd backend
pip install fastapi uvicorn supabase gpt4all pydantic python-jose passlib python-multipart redis python-dotenv
cd ..

# 3. Install GUI dependencies
cd gui
pip install PyQt6 requests python-dotenv
cd ..

# 4. Set up environment
cp .env.example .env

# 5. Run backend (Terminal 1)
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 6. Run GUI (Terminal 2, activate venv first)
source venv/bin/activate
cd gui
python main.py
```

## Quick Fix for PyQt6 Issues

Try this immediate fix:

```bash
# Stop the current process (Ctrl+C)
# Then run:
source venv/bin/activate
pip uninstall PyQt6 PyQt6-Qt6 PyQt6-sip -y
pip install PyQt6==6.5.3

# Try running again:
./run_app_fixed.sh
```

If PyQt6 still doesn't work, you can temporarily test the backend only:

```bash
# Just run the backend to test API
./run_backend_fixed.sh

# Then visit http://localhost:8000/docs to test the API
```

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Support

For issues or questions, check the logs in your terminal or create an issue in the project repository.
