import sys
from flask import Flask
from flask import request, render_template
from sqlalchemy.orm import sessionmaker
from rpf_spiders.rpf_spiders.models import RFP, PointOfContact, RFP_contacts,\
    db_connect, create_deals_table
from fbo_spider.models import *

# import sqlalchemy.orm
# sqlalchemy.orm.ScopedSession = sqlalchemy.orm.scoped_session
# from elixir import *
# from fbo_spider.models import OpportunityDetail
# from fbo_spider.db_config import user, password, host, database, port
#
#
# metadata.bind = "postgresql://{0}:{1}@{2}:{3}/{4}?client_encoding='utf-8'".format(user, password, host, port, database)

app = Flask(__name__)
sys.path.append(".")

@app.route('/')
def show_list_of_spiders():
    return render_template('main.html')

@app.route('/nasa', methods=['POST', 'GET'])
def show_results_nasa():

    engine = db_connect()
    create_deals_table(engine)
    Session = sessionmaker(bind=engine)
    sess = Session()
    if request.method == 'POST':
        search_code = request.form['naics']
        if not search_code:
            rfps = sess.query(RFP).all()
        else:
            rfps = sess.query(RFP).filter(RFP.NAICS_code == search_code).all()
    else:
        rfps = sess.query(RFP).all()

    return render_template('nasa.html', rfps=rfps)

@app.route('/fbo', methods=['POST', 'GET'])
def show_results_fbo():

    engine = db_connect()
    create_deals_table(engine)
    Session = sessionmaker(bind=engine)
    sess = Session()
    if request.method == 'POST':
        search_code = request.form['naics']
        if not search_code:
            rfps = OpportunityDetail.query.all()
        else:
            code = NAICSChild.query.filter_by(code=search_code).first()
            rfps = OpportunityDetail.query.filter_by(naics_code=code)\
                .all()
    else:

        rfps = OpportunityDetail.query.all()

    return render_template('fbo.html', rfps=rfps)



if __name__ == "__main__":
    setup_all()
    create_all()
    app.debug = True
    app.run(host='0.0.0.0')


