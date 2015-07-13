# -*- coding: utf-8 -*-
from sqlalchemy.orm import sessionmaker
from models import RFP, PointOfContact, RFP_contacts, db_connect, \
    create_deals_table


class RpfSpidersPipeline(object):
    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates tables.
        """
        engine = db_connect()
        create_deals_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        session = self.Session()
        rfp = RFP(title=item.get('title', ''),
                  URL=item.get('URL', ''),
                  posted=item.get('posted', None),
                  response_due=item.get('response_due', None),
                  classification_code=item.get('classification_code', ''),
                  NAICS_code=item.get('NAICS_code', ''),
                  set_aside_code=item.get('set_aside_code', ''),
                  contracting_office_address=item.get(
                      'contracting_office_address', ''),
                  description=item.get('description', ''),
                  )
        response_due = item.get('response_due', None)
        if rfp.response_due == "N/A":
            rfp.response_due = None
            response_due = None

        existing_query_rfp = session.query(RFP).filter(
            RFP.title == rfp.title, RFP.posted == rfp.posted).first()

        if existing_query_rfp:
            rfp = existing_query_rfp
            rfp.posted = item.get('posted', '')
            rfp.response_due = response_due
            rfp.classification_code = item.get('classification_code', '')
            rfp.NAICS_code = item.get('NAICS_code', '')
            rfp.set_aside_code = item.get('set_aside_code', '')
            rfp.contracting_office_address = item.get(
                     'contracting_office_address', '')
            rfp.description = item.get('description', '')

        else:
            session.add(rfp)
        session.commit()

        for contact in item.get('point_of_contact', []):
            poc = PointOfContact(name=contact['Name'],
                                 title=contact['Title'],
                                 phone=contact['Phone'],
                                 fax=contact['Fax'],
                                 email=contact['Email'])

            existing_query = session.query(PointOfContact).filter(
                PointOfContact.name == poc.name).first()
            if existing_query:
                poc = existing_query
                poc.title = contact['Title']
                poc.phone = contact['Phone']
                poc.fax = contact['Fax']
                poc.email = contact['Email']
                rfp.point_of_contact.append(poc)
                poc.rfp.append(rfp)
            else:
                rfp.point_of_contact.append(poc)
                poc.rfp.append(rfp)
                session.add(poc)

            session.commit()

        session.close()

        return item
