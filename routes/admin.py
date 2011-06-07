from app import app
from decorators import *

from extensions.FlaskSQLAlchemy import db
from extensions.FlaskUploads import electionHeader

from forms.election import *
from model import Election, Question, Answer

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
            'ELECTION_ADDED'            : u'Created new election.',
            'ELECTION_UPDATED'          : u'Election has been successfully updated.',
            'QUESTION_CANDIDATE_MORE'   : u'Added new candidate question with multiple answers',
            'QUESTION_CANDIDATE_SIMPLE' : u'Added new candidate question with single answer',
            'QUESTION_MORE'             : u'Added new question with multiple answers',
            'QUESTION_SIMPLE'           : u'Added new question with single answer',
            'QUESTION_UPDATED'          : u'The question has been successfully updated',
            'ANSWER_ADDED'              : u'Added new answer',
            }

ERROR_DICT = {
            'INPUTS'            : u'Incorrect inputs.',  
            'ELECTION_NONE'     : u'Not existing election', 
            'QUESTION_NONE'     : u'This question does not exist'               
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

"""

    Admin function for adding questions to election 
    Inputs: id_election(election ID)

    Description:
    - election summary with (candidate)question and answers

"""

@app.route('/admin/election/<int:id_election>/questions',methods=['GET', 'POST'])
@admin_required
def admin_questions(id_election):
    if request.method == 'POST':
        moreAnsw = candidates = False
        if request.form.get('more'):
            if unicode(request.form['more'])=='more':
                moreAnsw = True
        if request.form.get('candidate') and request.form['candidate']=="ok":
            candidates = True  
        count = 0
        if request.form.get('count'):
            try:
                count = int(unicode(request.form['count']))
            except:
                flash(QUESTION_INPUT,category='error')
                return redirect(url_for('admin_questions',id_election = id_election))

        db.session.add(Question(unicode(request.form['question']),id_election, count, moreAnsw, candidates))
        db.session.commit()

        if (candidates and moreAnsw):
            flash(INFO_DICT['QUESTION_CANDIDATE_MORE'])   
        elif (candidates):
            flash(INFO_DICT['QUESTION_CANDIDATE_SIMPLE'])  
        elif (moreAnsw):
            flash(INFO_DICT['QUESTION_MORE'])   
        else:
            flash(INFO_DICT['QUESTION_SIMPLE'])

    election = Election.query.filter_by(id = id_election).first()
    if election:
        questions = Question.query.filter_by(vid = id_election)   
        return render_template('admin/election/questions.html',election = election, questions = questions, question = QuestionField())

    flash(ERROR_DICT['ELECTION_NONE'],category = 'error')
    return redirect(url_for('admin_election'))  


"""

    Admin function for showing (candidate) questions of election to update
    Inputs: id_question(question ID)

Description:
    - show selected question to be updated
    - possibility add answers

"""

@app.route('/admin/election/question/<int:id_question>/edit', methods=['GET', 'POST'])
@admin_required
def admin_question_edit(id_question): 
    toEdit = Question.query.filter_by(id = id_question).first()
    if toEdit:
        if request.method == 'POST':    
            toEdit.text = unicode(request.form['question'])
            if request.form.get('more'):
                if unicode(request.form['more'])=='more':
                    toEdit.moreAnsw = True
                    try:
                        toEdit.count = int(unicode(request.form['count']))
                    except:
                        flash(ERROR_DICT['INPUT'],category='error')
                else:    
                    toEdit.moreAnsw = False
                if request.form.get('candidate'):
                    toEdit.candidate = True    
                db.session.commit()
                flash(INFO_DICT['QUESTION_UPDATED'])
            return redirect(url_for('admin_questions',id_election = toEdit.vid))        


        answers = Answer.query.filter_by(oid = id_question)
        return render_template('admin/election/answers.html', question = toEdit, answers = answers)

    flash(ERROR_DICT['QUESTION_NONE'],category = 'error')
    return redirect(url_for('admin_election'))
