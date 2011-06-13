from flask import render_template, flash, redirect, url_for, session, request

from app import app
from decorators import login_required
from model import User, Election, Question, Answer, Voting

from extensions.FlaskSQLAlchemy import db

INFO_DICT = {
             'VOTING_ADDED':       u'Thank You for voting.',
             'VOTING_UPDATE':      u'Thank You for updating your voting'
            }

"""

    Function for adding new user voter voting 
    Inputs:  id_election (election ID)

    Description:
    - show the election instances(questions, answers) with possibility to vote
    on POST: add user voting into db
    
"""

@app.route('/election/<int:id_election>/vote', methods=['GET', 'POST'])
@login_required
def election_voting(id_election):
    if request.method == 'POST':
        user = User.query.filter_by(username = session['user']).first()
        for new in request.form:                  
            fieldValue = request.form[new] 
            if (fieldValue.isdigit()): 
                n = Voting(user.id, fieldValue, id_election) 
                db.session.add(n)
        db.session.commit()
        flash(INFO_DICT['VOTING_ADDED']) 
        return redirect(url_for('election'))

    election    = Election.query.filter_by(id = id_election).first()
    questions   = Question.query.filter_by(vid = id_election)
    answers     = Answer.query.join((Question,Question.id == Answer.oid)).filter_by(vid = id_election)
    return render_template('election/voting.html', election = election, answers = answers, questions = questions)

"""

    Function for updating user voting on election
    Inputs:  id_election (election ID)

    Description:
    - delete all voted answers of user
    - insert new answers
    
"""

@app.route('/election/<int:id_election>/update', methods=['GET', 'POST'])
@login_required
def election_updating(id_election):
    user = User.query.filter_by(username = session['user']).first() 
    if request.method == 'POST':
        odv = Voting.query.filter_by(uid = user.id).filter_by(vid = id_election).delete()     
        db.session.commit()

        for newAdding in request.form:               
            fieldValue = request.form[newAdding] 
            if (fieldValue.isdigit()):
                n = Voting(user.id, fieldValue, id_election) 
                db.session.add(n)

        db.session.commit()
        flash(INFO_DICT['VOTING_UPDATE']) 
        return redirect(url_for('election'))
                        
    election    = Election.query.filter_by(id = id_election).first()
    questions   = Question.query.filter_by(vid = id_election)
    answers     = Answer.query.join((Question,Question.id == Answer.oid))

    myVoting = db.session.query(Voting.mid).filter_by(uid = user.id).filter_by(vid = id_election)    

    voted = list()
    for voting in myVoting:
        voted.append(voting.mid)    
    
    return render_template('election/voted.html', election = election, questions = questions, answers = answers, voted = voted)    
