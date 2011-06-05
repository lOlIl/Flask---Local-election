from app import app

from flask import render_template, flash

@app.route('/')
def index():
    flash(u'Test info message',category = 'info')
    flash(u'Test warning message',category = 'warning')
    flash(u'Test error message',category = 'error')
    return render_template('index.html')
