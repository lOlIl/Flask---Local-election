from app import *

import routes

if __name__ == '__main__':
    db.create_all()
    app.run(host=app.config['HOST'],port=app.config['PORT'])
