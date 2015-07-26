import sys
from flask import Flask
from flask import request, render_template
from sqlalchemy.orm import sessionmaker
from rpf_spiders.rpf_spiders.models import RFP, PointOfContact, RFP_contacts,\
    db_connect, create_deals_table
from fbo_spider.models import *

app = Flask(__name__)
sys.path.append(".")

setup_all()
create_all()
app.debug = True

@app.route('/')
def show_main():
    return render_template('main.html')

@app.route('/list')
def show_list_of_spiders():
    return render_template('list.html')

@app.route('/get_data', methods=['POST', 'GET'])
def get_data():
    engine = db_connect()
    create_deals_table(engine)
    Session = sessionmaker(bind=engine)
    sess = Session()
    if request.method == 'POST':
        search_code = request.form['naics']
        if not search_code:
            rfps_nasa = sess.query(RFP).all()
        else:
            rfps_nasa = sess.query(RFP).filter(RFP.NAICS_code == search_code).all()
    else:
        rfps_nasa = sess.query(RFP).all()

    engine = db_connect()
    create_deals_table(engine)
    Session = sessionmaker(bind=engine)
    sess = Session()
    if request.method == 'POST':
        search_code = request.form['naics']
        if not search_code:
            rfps_fbo = OpportunityDetail.query.all()
        else:
            code = NAICSChild.query.filter_by(code=search_code).first()
            rfps_fbo = OpportunityDetail.query.filter_by(naics_code=code)\
                .all()
    else:
        rfps_fbo = OpportunityDetail.query.all()

    res = []
    for r in rfps_nasa:
        res.append(r.to_json())
    for r in rfps_fbo:
        res.append(r.to_json())
    return str(res)

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
    app.run(host='0.0.0.0')


