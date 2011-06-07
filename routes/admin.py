from app import app
from decorators import *

from extensions.FlaskSQLAlchemy import db
from forms.election import *

from model import Election

from string import atoi
from time import strptime
from datetime import datetime

"""

    Admin function for basic admin menu
    Inputs:  -

    Description:
    - show the elements in admin menu

"""

INFO_DICT = {
            'ELECTION_ADDED'    : u'Created new election.',
            }

ERROR_DICT = {
            'INPUTS'            : u'Incorrect inputs.',                  
            }

@app.route('/admin')
@admin_required
def admin():
    return render_template('admin/menu.html')

@app.route('/admin/election', methods=['GET', 'POST'])
@admin_required
def admin_election():
    if request.method == 'POST':  
        name = unicode(request.form['name'])
        desc = unicode(request.form['desc'])

        try:        
            start = datetime.strptime(
                                        unicode(request.form['start'])+' '+\
                                        unicode(request.form['startTime_hod'])+':'+\
                                        unicode(request.form['startTime_min'])+':00',\
                                        '%Y-%m-%d %H:%M:%S')
        except:
            start = None

        try:
            end = datetime.strptime(
                                        unicode(request.form['end'])+' '+\
                                        unicode(request.form['endTime_hod'])+':'+\
                                        unicode(request.form['endTime_min'])+':00',\
                                        '%Y-%m-%d %H:%M:%S') 
        except:
            end = None

        show = False
        if request.form.get('show') != "None": 
            show = True
            flash(show)

        if start != None and end != None and name != "":
            db.session.add(Election(name, desc, start, end, show))
            db.session.commit()
            flash(INFO_DICT['ELECTION_ADDED'])
        else:
            flash(ERROR_DICT['INPUTS'])

    inputs = dict([ ('name',        ElectionNameField()),
                    ('desc',        ElectionDescField()),
                    ('start',       ElectionStartField()),
                    ('startTime',   ElectionStartTimeField()),
                    ('end',         ElectionEndField()),
                    ('endTime',     ElectionEndTimeField()),
                    ('show',        ElectionShowField())
                 ])
    all_elections = Election.query.all()
    return render_template('admin/election/main.html', input = inputs, elections = all_elections)
