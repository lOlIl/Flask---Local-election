from flask import render_template, flash, redirect, url_for, session, request

from app import app
from forms import LoginField, PasswordField
from model import User, Election

from extensions.LDAP import check_pw_ldap
from extensions.FlaskSQLAlchemy import db

INFO_DICT = {
             'ADMIN':       u'Welcome back, Admin %s',
             'ADMIN_LDAP':  u'Welcome back, LDAP Admin %s',
             'USER':        u'Welcome back, user %s',
             'USER_LDAP':   u'Welcome back, LDAP user %s',
             'LOGOUT':      u'You have been successfully logged out!'  
            }

ERROR_DICT = {
              'NOUSER':u"This user doesn't exist",
              'BADPW':u'Incorrect password',
              'NOACT':u"Your account wasn't activated yet.",
              'EMPTY':u'The login requires non-empty username and password field'
             }

"""

    Index function of webside
    Inputs: -

    Description:
    - the main side of application
    - redirected in many cases

"""

@app.route('/')
def index():
    return render_template('index.html')

"""

    Login function of webside
    Inputs: form username and password

    Description:
    - 

"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = error_local = error_global = False
    if request.method == 'POST':
        user = unicode(request.form['username'])
        pwd  = unicode(request.form['password'])

        if user == "" or pwd == "":
            flash(ERROR_DICT['EMPTY'],category = 'warning')
            return redirect(url_for('login')) 

        local_user = User.query.filter_by(username='%s' %user).first()  
        if local_user and local_user.confirm_status=='confirmed': 
            if not local_user.check_password(pwd):
                error_local = 'BADPW'
        else:
            if not local_user or local_user.confirm_status=='ldap':
                error_local = 'NOUSER'        

        ldapuser=False                        
        if error_local=='NOUSER' and app.config['LDAP']:
            error_ldap = False           
            result_ldap = check_pw_ldap(user,pwd)
            try:
                umail, usname = result_ldap   
                ldapuser = True
                error_global = False
            except:
                error_ldap = result_ldap        
                error_global = error_ldap 
        elif error_local:
            error_global = error_local

        if not error_global:
            if not ldapuser:
                if local_user.confirm_status != "confirmed":                    # local user without mail activation   
                    flash(ERROR_DICT['NOACT'],category = 'warning')
                else:                                                           # local user with correct password    
                    session['user'] = local_user.username

            else:                                                               # LDAP verified user
                session['user'] = user
                user_exists = User.query.filter_by(mail='%s' %umail).first()
                if user_exists and user_exists.confirm_status != "ldap":        # LDAP user invited for voting by admin via MAIL
                    user_exists.name = usname
                    user_exists.username = user
                    user_exists.confirm_status = 'ldap'
                    db.session.commit()

                elif not user_exists:                                           # 1st time LDAP login
                    db.session.add(User(user,umail,umail,'ldap',usname))
                    db.session.commit()

            if session.get('user'):   
                if (session['user'] in app.config['ADMINS']):
                    session['admin'] = session['user'] 
                    flash(INFO_DICT['ADMIN_LDAP'] % user) if ldapuser else flash(INFO_DICT['ADMIN'] % user)
                else:
                    flash(INFO_DICT['USER_LDAP'] % user) if ldapuser else flash(INFO_DICT['USER'] % user)
                return redirect(url_for('index'))         
            
        else:
            flash(ERROR_DICT[error_global],category = 'error')
            return redirect(url_for('login'))     

    inputs = dict([('login',LoginField()),('pass',PasswordField())])
    return render_template('user/login.html', input = inputs)

"""

    Logout function
    Inputs: -

    Description:
    - logout from application
    - delete user (and admin) session
    - redirect to index page

"""

@app.route('/logout')
def logout():
    if session.get('admin'):
        session.pop('admin', None)    
    if session.get('user'):
        session.pop('user', None)
        flash(INFO_DICT['LOGOUT'])

    return redirect(url_for('index'))

@app.route('/election')
def election():
    all_elections = Election.query.all()
    return render_template('election/index.html', elections = all_elections)
