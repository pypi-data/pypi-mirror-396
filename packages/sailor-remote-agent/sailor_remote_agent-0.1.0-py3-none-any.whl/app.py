#!/usr/bin/env python3
"""Minimal Bottle web app for clipboard and evaluation operations."""

import ast
import subprocess
from bottle import Bottle, request, response, template, run
import os

app = Bottle()

# In-memory storage
clipboard_history = []
evaluation_results = []


@app.route('/ping', method='GET')
def ping():
    """Health check endpoint."""
    response.content_type = 'application/json'
    return {'pong': 'ok'}


@app.route('/clipboard', method='POST')
def clipboard():
    """Store clipboard content and execute xclip command."""
    try:
        data = request.json
        if not data or 'content' not in data:
            response.status = 400
            return {'error': 'Missing content field'}
        
        clipboard_content = data['content']
        # Replace single quotes with escaped version
        clipboard_content = clipboard_content.replace("'", "'\\''")
        
        # Execute xclip command
        command = f"echo -n '{clipboard_content}' | xclip -selection clipboard &"
        subprocess.Popen(command, shell=True)
        
        response.content_type = 'application/json'
        return {'status': 'ok'}
    except Exception as e:
        response.status = 500
        return {'error': str(e)}


@app.route('/evaluate', method='POST')
def evaluate():
    """Safely evaluate Python literal expression."""
    try:
        data = request.json
        if not data or 'expr' not in data:
            response.status = 400
            return {'error': 'Missing expr field'}
        
        expr = data['expr']
        # Safely evaluate using ast.literal_eval
        result = ast.literal_eval(expr)
        
        # Store result
        evaluation_results.append({
            'expr': expr,
            'result': result
        })
        
        response.content_type = 'application/json'
        return {'status': 'ok', 'result': result}
    except (ValueError, SyntaxError) as e:
        response.status = 400
        return {'error': f'Invalid expression: {str(e)}'}
    except Exception as e:
        response.status = 500
        return {'error': str(e)}

@app.route('/answer', method='GET')
def answer():
    """Render HTML showing the latest evaluation result."""
    if not evaluation_results:
        latest = None
    else:
        latest = evaluation_results[-1]
    return template('answer', latest=latest)


@app.route('/result', method='GET')
def result():
    """Render HTML showing all evaluation results."""
    return template('result', results=evaluation_results)


def main():
    """Entry point for console script."""
    # Set template lookup path to views directory
    views_path = os.path.join(os.path.dirname(__file__), 'views')
    app.template_lookup = [views_path]
    # Use port 8081 if 8080 is unavailable, or allow override via environment variable
    run(app, host='localhost', port=8080, debug=True)


if __name__ == '__main__':
    main()
