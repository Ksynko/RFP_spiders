import warnings

import sqlalchemy.orm
sqlalchemy.orm.ScopedSession = sqlalchemy.orm.scoped_session
# from sqlalchemy import UniqueConstraint
from sqlalchemy.exc import SAWarning
from elixir import *
from datetime import datetime
from db_config import user, password, host, database, port


metadata.bind = "postgresql://{0}:{1}@{2}:{3}/{4}?client_encoding='utf-8'".format(user, password, host, port, database)
# metadata.bind.echo = True
warnings.simplefilter('ignore', SAWarning)

class Summary(Entity):
    using_options(tablename='summary')
    url = Field(Unicode(1000), unique=True)
    state = Field(Unicode(255))
    is_processed = Field(Boolean, default=False)
    date_entered = Field(DateTime, default=datetime.utcnow())
    date_processed = Field(DateTime, nullable=True)
    category = Field(Unicode(255))
    category_id = Field(Unicode(50), default='')
    # using_table_options(UniqueConstraint('date', 'notifier', 'h', 'm', 'r', 'l', 'domain', 'os', 'view'))


class OpportunityDetail(Entity):
    using_options(tablename='opportunity_detail')
    url = Field(Unicode(1000), unique=True)
    name = Field(Unicode(1000))
    sol_num = Field(Unicode(100))
    agency = Field(Unicode(1000))
    office = Field(Unicode(1000))
    location = Field(Unicode(1000))
    notice_type = Field(Unicode(500))
    original_posted_date = Field(DateTime, nullable=True)
    posted_date = Field(DateTime, nullable=True)
    response_date = Field(Unicode(200))
    original_response_date = Field(Unicode(200))
    archiving_policy = Field(Unicode(500))
    original_archive_date = Field(DateTime, nullable=True)
    archive_date = Field(DateTime, nullable=True)
    original_set_aside = Field(Unicode(200))
    set_aside = Field(Unicode(200))
    classification_code_num = Field(Unicode(50))
    classification_code_desc = Field(Unicode(200))
    naics_code = ManyToOne('NAICSChild')
    synopsis = Field(UnicodeText)
    contracting_office_address = Field(UnicodeText)
    place_of_performance = Field(UnicodeText)
    primary_poc = Field(UnicodeText)
    secondary_poc = Field(UnicodeText)
    state = Field(Unicode(255))
    category = Field(Unicode(255))
    category_id = Field(Unicode(50))

    date_entered = Field(DateTime, default=datetime.utcnow())

    def to_json(self):
        return dict(url=self.url,
                    name=self.name,
                    sol_num=self.sol_num,
                    agency=self.agency,
                    office=self.office,
                    location=self.location,
                    notice_type=self.notice_type,
                    original_posted_date=self.original_posted_date,
                    posted_date=self.posted_date,
                    response_date=self.response_date,
                    original_response_date=self.original_response_date,
                    archiving_policy=self.archiving_policy,
                    original_archive_date=self.original_archive_date,
                    archive_date=self.archive_date,
                    original_set_aside=self.original_set_aside,
                    classification_code_num=self.classification_code_num,
                    classification_code_desc=self.classification_code_desc,
                    naics_code=self.naics_code,
                    synopsis=self.synopsis,
                    contracting_office_address=self.contracting_office_address,
                    place_of_perfomance=self.place_of_performance,
                    primary_poc=self.primary_poc,
                    secondary_poc=self.secondary_poc,
                    state=self.state,
                    category=self.category,
                    category_id=self.category_id,
                    date_entered=self.date_entered
                    )


class NAICSParent(Entity):
    using_options(tablename='naics_parent')
    code = Field(Unicode(100), unique=True)
    desc = Field(Unicode(1000))
    child_codes = OneToMany('NAICSChild')

    def to_json(self):
        return dict(code=self.code)


class NAICSChild(Entity):
    using_options(tablename='naics_child')
    code = Field(Unicode(100), unique=True)
    desc = Field(Unicode(1000))
    parent_code = ManyToOne('NAICSParent')

    def to_json(self):
        return dict(code=self.code)