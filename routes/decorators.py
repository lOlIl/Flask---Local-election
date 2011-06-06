# Aplikacia a konfiguracia
from app import app

# importy pre Flask - mozno viac vhodne do app
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

# decorators - Wrapp
from functools import wraps

# DECORATORS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if (not session.get('user')):
            flash(u'Nutne uzivatelske prihlasenie')            
            return redirect(url_for("login")) 
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if ((not session.get('user')) or (session['user'] not in app.config['ADMINS'])):
            flash(u'Nutne administratorske prava')            
            return redirect(url_for("login")) 
        return f(*args, **kwargs)
    return decorated_function
