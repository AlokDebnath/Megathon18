from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///jobs.db', echo=True)
Base = declarative_base()
Session = sessionmaker()

class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    job_id = Column(String)
    company = Column(String)
    title = Column(String)
    description = Column(Text)
    category = Column(String)
    ttype = Column(String)
    sponsored_only = Column(String)
    url = Column(String)
    valid = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    zip_code = Column(String)
    original_url = Column(String)
    created_at = Column(String)
    pub_date = Column(String)
    updated_at = Column(String)
    ref_num = Column(String)

    def __repr__(self):
        return '<Job %s at %s>' % (self.job_id, self.company)

def parse(fname, session):
    s = ""
    in_field = False
    acc = []
    i = 0
    skip = False    
    with open(fname) as f:
        for line in f:
            for c in line:
                if c == '"':
                    if in_field:
                        acc.append(s)
                        in_field = False
                        s = ''
                        
                        if len(acc) >= 19:
                            skip = True
                    else:
                        in_field = True
                elif c == '\n':
                    if in_field:
                        s += ' '
                    else: 
                        if not skip:
                            i += 1
                            session.add(Job(job_id = acc[0], 
                                            company = acc[1], 
                                            title = acc[2], 
                                            description = acc[3], 
                                            category = acc[4], 
                                            ttype = acc[5], 
                                            sponsored_only = acc[6], 
                                            url = acc[7],
                                            valid = acc[8],
                                            city = acc[9],
                                            state = acc[10],
                                            country = acc[11],
                                            zip_code = acc[12],
                                            original_url = acc[13],
                                            created_at = acc[14],
                                            pub_date = acc[15],
                                            updated_at = acc[16],
                                            ref_num = acc[17]))
                            print("Job added! %d" % i)
                            if i % 1000 == 0:
                                session.commit()
                        skip = False
                        acc = []
                else:
                    if in_field:
                        s += c
        session.commit()
    print("Done")


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    Session.configure(bind=engine)
    session = Session()
    parse('jobs.csv', session)
