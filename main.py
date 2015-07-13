import sys
from flask import Flask
from flask import request, render_template
from sqlalchemy.orm import sessionmaker
from rpf_spiders.rpf_spiders.models import RFP, PointOfContact, RFP_contacts,\
    db_connect, create_deals_table
app = Flask(__name__)
sys.path.append(".")

@app.route('/', methods=['POST', 'GET'])
def show_results():

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

    return render_template('main.html', rfps=rfps)


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')

