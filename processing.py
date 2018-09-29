from jobdb import *
import nltk
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///jobs.db')
Base = declarative_base()
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

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

def noun_finder(tokenized_words):
    # NN is more generic, NNP is more specific. Check which one yields better performance
    l1 = ['>', '<', 'nbsp']
    tokenized_words = [x for x in tokenized_words if x not in l1 and len(x) > 2 and x[0] != '/'] 
    is_noun = lambda pos: pos[:3] == 'NNP'
    #is_noun = lambda pos: pos[:2] == 'NN'
    nouns = [word for (word, pos) in nltk.pos_tag(tokenized_words) if is_noun(pos)] 
    return nouns

# For Data input, need to tokenize it then run noun finder


def score_2_list(nounlist1, nounlist2):
    score = 0
    nounhash = {}
    for noun in nounlist1:
        if noun not in nounhash.keys():
            nounhash[noun] = 1
        else:
            nounhash[noun] += 1
    for noun in nounlist2:
        if noun not in nounhash.keys():
            nounhash[noun] = 1
        else:
            nounhash[noun] += 1
    for i in nounhash.keys():
        if nounhash[i] > 1:
            score += 1
    return score

def score_3_list(nounlist1, nounlist2, nounlist3):
    for noun in nounlist1:
        if noun not in nounhash.keys():
            nounhash[noun] = 1
        else:
            nounhash[noun] += 1
    for noun in nounlist2:
        if noun not in nounhash.keys():
            nounhash[noun] = 1
        else:
            nounhash[noun] += 1
    for noun in nounlist3:
        if noun not in nounhash.keys():
            nounhash[noun] = 1
        else:
            nounhash[noun] += 1
    for i in nounhash.keys():
        if nounhash[i] == 2:
            score += 1
        if nounhash[i] == 3:
            score += 10
    return score

def getJobDesc():
    job_desclist = []
    for i in session.query(Job).order_by(Job.id):
        job_desclist.append([i.description, i.id])
    return job_desclist


def read_job_desc():
    joblist = getJobDesc()
    titlemap = []
    # joblist is a list of lists where the nested list is [job_title, job_description]
    counter = 0
    for job in joblist:
        counter += 1
        titlemap.append([job[1], noun_finder(nltk.word_tokenize(job[0]))]) # job[0] is always the description
        if counter == 100:
            break
    return titlemap 

if __name__ == '__main__':
    a = read_job_desc()
