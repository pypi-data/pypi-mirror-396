# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

streamlit-firebase-auth is a Streamlit component library that provides Firebase Authentication widgets (login, logout, session management, signup, password reset) for Streamlit apps.

## Build & Development Commands

### Frontend (React/TypeScript)
```bash
cd streamlit_firebase_auth/frontend
npm install          # Install dependencies
npm run start        # Start dev server on port 3001
npm run build        # Build for production
npm run test         # Run Jest tests
```

### Python Package
```bash
python -m build      # Build package (requires frontend build first)
twine upload dist/*  # Publish to PyPI
```

### Running the Example
```bash
# Development mode (uses frontend dev server)
export PYTHONPATH="$(pwd):$PYTHONPATH"
# Set release=False in _get_component_func() in __init__.py
streamlit run example/app.py

# Production mode
# Set release=True in _get_component_func() in __init__.py
streamlit run example/app.py
```

## Architecture

### Python Backend (`streamlit_firebase_auth/__init__.py`)
- `FirebaseAuth` class: Main interface exposing `login_form()`, `logout_form()`, `check_session()`, `signup()`, `send_password_reset_email()`
- Uses `streamlit-component-lib` to communicate with React frontend
- `signup()` uses `firebase-admin` SDK (server-side) for user creation
- Supports English (`en`) and Japanese (`jp`) localization

### React Frontend (`streamlit_firebase_auth/frontend/src/Auth.tsx`)
- Single `Auth` component that renders different sub-components based on `name` prop:
  - `LoginForm`: Email/password and Google OAuth login
  - `LogoutForm`: Logout button
  - `CheckSession`: Session validation (invisible component)
  - `SendPasswordResetEmail`: Password reset button
- Uses Firebase client SDK for authentication
- UI built with MUI (Material-UI)
- Communicates results back to Python via `Streamlit.setComponentValue()`

### Dev/Prod Toggle
The `_get_component_func(release=True)` function in `__init__.py` controls whether the component loads from the dev server (port 3001) or the built static files. Toggle `release=False` for development.
