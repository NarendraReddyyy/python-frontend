#!/usr/bin/env python3
"""
Flask Frontend for User Management System
Serves HTML templates and handles API calls to backend
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import requests
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL')
app.config['API_BASE_URL'] = API_BASE_URL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Frontend starting with API_BASE_URL: {API_BASE_URL}")

def make_api_request(method, endpoint, data=None):
    """Make API request to backend"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10)
        elif method == 'PUT':
            response = requests.put(url, json=data, timeout=10)
        elif method == 'DELETE':
            response = requests.delete(url, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        return None

@app.route('/')
def index():
    """Main page - display users"""
    try:
        response = make_api_request('GET', '/users')
        if response and response.status_code == 200:
            users_data = response.json()
            users = users_data.get('data', [])
        else:
            users = []
            flash('Failed to load users from API', 'error')
    except Exception as e:
        logger.error(f"Error loading users: {e}")
        users = []
        flash('Error connecting to backend API', 'error')
    
    return render_template('index.html', users=users, api_url=API_BASE_URL)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """Add new user"""
    if request.method == 'POST':
        user_data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'age': int(request.form.get('age')) if request.form.get('age') else None
        }
        
        response = make_api_request('POST', '/users', user_data)
        if response and response.status_code == 201:
            flash('User created successfully! 🎉', 'success')
            return redirect(url_for('index'))
        else:
            error_msg = 'Failed to create user'
            if response:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', error_msg)
                except:
                    pass
            flash(f'Error: {error_msg}', 'error')
    
    return render_template('add_user.html')

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    """Edit existing user"""
    if request.method == 'POST':
        user_data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'age': int(request.form.get('age')) if request.form.get('age') else None
        }
        
        response = make_api_request('PUT', f'/users/{user_id}', user_data)
        if response and response.status_code == 200:
            flash('User updated successfully! ✅', 'success')
            return redirect(url_for('index'))
        else:
            error_msg = 'Failed to update user'
            if response:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', error_msg)
                except:
                    pass
            flash(f'Error: {error_msg}', 'error')
    
    # Get user data for editing
    response = make_api_request('GET', f'/users/{user_id}')
    if response and response.status_code == 200:
        user_data = response.json()
        user = user_data.get('data')
    else:
        flash('User not found', 'error')
        return redirect(url_for('index'))
    
    return render_template('edit_user.html', user=user)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """Delete user"""
    response = make_api_request('DELETE', f'/users/{user_id}')
    if response and response.status_code == 200:
        flash('User deleted successfully! 🗑️', 'success')
    else:
        flash('Failed to delete user', 'error')
    
    return redirect(url_for('index'))

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        response = make_api_request('GET', '/')
        if response and response.status_code == 200:
            backend_status = 'healthy'
        else:
            backend_status = 'unhealthy'
    except:
        backend_status = 'unreachable'
    
    return jsonify({
        'frontend': 'healthy',
        'backend': backend_status,
        'api_url': API_BASE_URL
    })

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)