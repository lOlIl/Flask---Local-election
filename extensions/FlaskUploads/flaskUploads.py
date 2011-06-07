from app import app

from flaskext.uploads import configure_uploads, UploadSet

electionHeader = UploadSet('election', app.config['UPLOADS_DEFAULT_DEST'])
configure_uploads(app, (electionHeader))
