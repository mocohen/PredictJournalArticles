from crossref.restful import Works, Etiquette, Journals
import sqlite3
import time




# class object for Crossref
class DOIRetreiver(object):
    def __init__(self):
        self.etiquette = Etiquette('Voth Group Readings', '0.0alpha', 'My Project URL', 'mocohen@uchicago.edu')
        self.retreiver = Works(etiquette=self.etiquette)

    def set_etiquette(self, projectName, projectVersion, projectURL, emailAddress):
        self.etiquette = Etiquette(projectName, projectVersion, projectURL, emailAddress)
        set_retreiver()

    def set_retreiver(self):
        self.retreiver = Works(etiquette=self.etiquette)

    def retreive_record(self, doi):
        record_dict = self.retreiver.doi(doi)
        return record_dict


# create tables in DB
def create_db(db_conn):
    c = db_conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS Articles
                (key        INTEGER  PRIMARY KEY,
                title     TEXT,
                journal   TEXT,
                publisher TEXT,
                page      TEXT,
                volume    TEXT,
                issue     TEXT,
                DOI       TEXT,
                ISSN      TEXT,
                isVoth    INT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS Authors
        (key        INTEGER  PRIMARY KEY,
            firstName   TEXT,
            lastName    TEXT,
            orcid       TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS ArticleAuthors
        (key INTEGER  PRIMARY KEY,
            authorID INTEGER,
            articleID INTEGER)''')
    db_conn.commit()


#Check to see if record exists
#if record does not exist, add to DB
def check_and_add(db_conn, journal_record, isVoth=False):

    # print(journal_record.keys())
    # print(journal_record)
    # raise('Error')

    c = db_conn.cursor()
    article_id = -1

    doi = journal_record['DOI']
    c.execute('SELECT key FROM Articles WHERE DOI=?', (doi,))
    result = c.fetchone()
    if result is not None:
        article_id = result[0]  

    if article_id < 0:
        add_to_db(db_conn, journal_record, isVoth)


#Add record to DB
def add_to_db(db_conn, journal_record, isVoth=False):

    if 'author' in journal_record:

        c = db_conn.cursor()


        journal = ''
        issue = ''
        page = ''
        volume = ''
        issn = ''
        title = journal_record['title'][0]
        publisher = journal_record['publisher']
        doi = journal_record['DOI']
        if 'container-title' in journal_record and len(journal_record['container-title']) > 0:
            journal = journal_record['container-title'][0]
        else:
            journal =journal_record['institution']['name']   
        if 'page' in journal_record:
            page = journal_record['page']
        if 'issue' in journal_record:
            issue = journal_record['issue']
        if 'volume' in journal_record:
            volume = journal_record['volume']
        if 'ISSN' in journal_record:
            issn = journal_record['ISSN'][0]
        c.execute('INSERT INTO Articles (title ,journal, publisher, page, volume, issue, isVoth, DOI, ISSN) VALUES (?,?,?,?,?,?,?,?,?)', 
            (title, journal, publisher, page, volume, issue, int(isVoth), doi, issn))
        c.execute('SELECT key FROM Articles WHERE DOI=?', (doi,))
        article_id = c.fetchone()[0]

        #raise('Error')

        

        for author in journal_record['author']:
            #print(author)
            author_id = -1
            fname = ''
            lname = ''
            if 'given' in author:
                fname = author['given']
            if 'family' in author:
                lname = author['family']

            if len(fname+lname) == 0:
                if 'name' in author:
                    lname = author['name']


            if 'suffix' in author:
                lname += ' ' + author['suffix']
            orcid = ''
            if 'ORCID' in author:
                orcid = author['ORCID']

                # select to see if orcid exists in database
                # set author_id
                c.execute('SELECT key FROM Authors WHERE orcid =?', (orcid,))

                result = c.fetchone()
                if result is not None:
                    #print(result)
                    author_id = result[0]
            else:
                c.execute('SELECT key FROM Authors WHERE firstName=? AND lastName=? AND orcid =?', (fname, lname, orcid))
                result = c.fetchone()
                if result is not None:
                    #print(result, fname, lname, orcid)
                    author_id = result[0]


            if author_id < 0:
                c.execute('INSERT INTO Authors (firstName, lastName, orcid) VALUES (?,?,?)', (fname, lname, orcid))
                c.execute('SELECT key FROM Authors WHERE firstName=? AND lastName=? AND orcid =?', (fname, lname, orcid))
                author_id = c.fetchone()[0]

            c.execute('INSERT INTO ArticleAuthors (authorID, articleID) VALUES (?,?)', (author_id, article_id))


        db_conn.commit()


# Add to DB all articles from a given journal between a date range
def add_all_journal_articles(db_conn, journal_issn, from_date, end_date):

    journals = Journals()
    dois = journals.works(journal_issn).filter(from_created_date=from_date, until_created_date=end_date)
    for record in dois:
        check_and_add(db_conn, record, isVoth=False)


# retreive a list of all the journals in the database
def retreive_all_journals(db_conn):
    c = db_conn.cursor()
    journals = []
    for row in c.execute('SELECT journal, ISSN FROM Articles WHERE isVoth=1 GROUP BY journal ORDER BY journal ASC'):
        journals.append((row[0], row[1]))

    return journals


# Using DOIs from file, retreive records from crossref and add to DB
def add_dois_from_file(db_conn, doi_file):
    input_dois = open(doi_file, 'r')

    for i, line in enumerate(input_dois):
        print('record %d' % (i))

        #be nice to the server. it does not seem to handle quick requests very well
        time.sleep(.5)
        if not '#' in line[:2]:
            strip = line.strip()
            #print(works.doi(line.strip()))

            num_tries = 0
            while num_tries < 3:
                try:
                    my_dict = doi_retreiver.retreive_record(strip)
                    num_tries=3
                except(TimeoutError, ConnectionError):
                    print('num tries %d, doi: %s' % (num_tries, strip))
                    num_tries += 1

            if my_dict is not None:

                if ('message' not in my_dict):
                    add_to_db(conn, my_dict, isVoth=True)
            else:
                bad_dois.append(strip)

    print(bad_dois)


if __name__ == "__main__":
	last = ''

	doi_retreiver = DOIRetreiver()

	bad_dois = []
	db_file = 'test.db'
	conn = sqlite3.connect(db_file)


	create_database = False
	if create_database:
		create_db(conn)
		add_dois_from_file(conn, 'doi_files/dois.dat')

	for journal, issn in retreive_all_journals(conn):
		print(journal, issn)
		if journal[0] >= 'P':
			add_all_journal_articles(conn, issn, '2017-01-01', '2018-05-31')




