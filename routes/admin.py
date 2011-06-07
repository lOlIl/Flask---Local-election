from app import app
from decorators import *

from extensions.FlaskSQLAlchemy import db
from extensions.FlaskUploads import electionHeader

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
            'ELECTION_UPDATED'  : u'Election has been successfully updated.'
            }

ERROR_DICT = {
            'INPUTS'            : u'Incorrect inputs.',  
            'ELECTION_NONE'     : u'Not existing election'                    
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
    for election in all_elections:
        if election.photo:
            election.photo = electionHeader.url(election.photo)    
    return render_template('admin/election/main.html', input = inputs, elections = all_elections)

"""

    Admin function for updating election
    Inputs: id_election(election ID)

    Description:
    - show selected election in form

    on POST: update the election fields, if there are correct inputs.
    
"""

@app.route('/admin/election/<int:id_election>/update', methods=['GET', 'POST'])
@admin_required
def admin_election_update(id_election):
    election = Election.query.filter_by(id = id_election).first()
    if election:
        if request.method == 'POST':    
            election.title =    unicode(request.form['name'])
            election.text =     unicode(request.form['desc'])

            if request.form.get('show') and request.form['show'] == 'checked':
                election.show = True
            else:
                election.show = False
            
            try:
                election.date_from = datetime.strptime(
                                        unicode(request.form['start'])+' '+\
                                        unicode(request.form['startTime_hod'])+':'+\
                                        unicode(request.form['startTime_min'])+':00',
                                        '%Y-%m-%d %H:%M:%S')    
                election.date_to = datetime.strptime(
                                        unicode(request.form['end'])+' '+\
                                        unicode(request.form['endTime_hod'])+':'+\
                                        unicode(request.form['endTime_min'])+':00',
                                        '%Y-%m-%d %H:%M:%S')          
                db.session.commit()        
                flash(INFO_DICT['ELECTION_UPDATED'])     
            except:
                flash(ERROR_DICT['INPUTS'])
            return redirect(url_for('admin_election'))

        inputs = dict([ 
                    ('name',        ElectionNameField()),
                    ('desc',        ElectionDescField()),
                    ('start',       ElectionStartField()),
                    ('startTime',   ElectionStartTimeField()),
                    ('end',         ElectionEndField()),
                    ('endTime',     ElectionEndTimeField()),
                    ('show',        ElectionShowField())
                 ])

        inputs['name'].value = election.title
        inputs['desc'].value = election.text

        if election.show:
            inputs['show'].checked = "yes"

        x = election.date_from
        inputs['start'].value = x.strftime('%Y-%m-%d')
        inputs['startTime'].value_1 = atoi(x.strftime('%H'))
        inputs['startTime'].value_2 = atoi(x.strftime('%M'))

        x = election.date_to
        inputs['end'].value = x.strftime('%Y-%m-%d')
        inputs['endTime'].value_1 = atoi(x.strftime('%H'))
        inputs['endTime'].value_2 = atoi(x.strftime('%M'))

        all_elections = Election.query.all()

        return render_template('admin/election/main.html', elections = all_elections, input = inputs, id_election = election.id)

    flash(ERROR_DICT['ELECTION_NONE'],category = 'error')
    return redirect(url_for('admin_election'))

"""

    Admin function for uploading election header 
    Inputs: id_election(election ID)

    Description:
    - election header saved into app
    - used Flask-Uploads
    - correct Election and selected photo file

"""

@app.route('/admin/volby/<int:id_election>/upload', methods=['POST'])
@admin_required
def admin_election_upload(id_election):
    election = Election.query.filter_by(id = id_election).first()
    if request.method == 'POST' and election and 'photo' in request.files:
        header = electionHeader.save(request.files['photo'])
        election.photo = header
        db.session.commit()
    return redirect(url_for('admin_election'))    
