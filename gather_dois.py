from string import punctuation
import re

def each_chunk(stream, separator):
  buffer = ''
  CHUNK_SIZE = 4096

  while True:  # until EOF
    chunk = stream.read(CHUNK_SIZE)  # I propose 4096 or so
    if not chunk:  # EOF?
      yield buffer
      break
    buffer += chunk
    while True:  # until no separator is found
      try:
        part, buffer = buffer.split(separator, 1)
      except ValueError:
        break
      else:
        yield part

def get_doi(stream):
    doi_loc = stream.find('10.1')
    if doi_loc >= 0:
        doi = stream[doi_loc:].split()[0]
        return doi.rstrip(punctuation).split(',')[0]
    else:
        arxiv_loc = stream.find('arxiv.org')
        if arxiv_loc >= 0:
            doi = stream[arxiv_loc:].split()[0]
            return doi.rstrip(punctuation)
    return None

def get_title(stream):
    title_loc = stream.find('Title')
    if title_loc >= 0:
        title = stream[title_loc:].split('\n')[0][7:].strip()
        if len(title) < 200:
            return title
    return None    

def read_csv(filename, debug=False):

    numDOIs = 0
    numNoDOIs = 0
    numMo = 0

    doi_list = []
    with open(filename) as myFile:
      for chunk in each_chunk(myFile, separator='\",\"'):
        doi = get_doi(chunk)
        if doi is not None:
            doi_list.append(doi)
            #print(doi.rstrip(punctuation))
            numDOIs += 1
        else:
            if '(1)' in chunk:
                numMo += 1
            elif 'Title' in chunk:
                print(get_title(chunk))
            else:
                if debug:
                    print(chunk)
                numNoDOIs += 1

    return (doi_list, numDOIs, numNoDOIs)

def read_bib(filename):
    numArticles = 0
    numDOIs = 0
    doi_list = []
    with open(filename) as myFile:
        for line in myFile:
            if '@article' in line:
                numArticles += 1
            if len(line) > 3 and 'doi' in line[:3]:
                doi_loc = line.find('10.1')
                doi = line[doi_loc:].split()[0]
                doi_list.append(doi.rstrip(punctuation))
                numDOIs += 1
    return (doi_list, numDOIs, numArticles - numDOIs)

def write_dois_to_file(filename, doi_list):
    with open(filename, 'w') as outFile:
        for doi in doi_list:
            outFile.write('%s\n' % (doi))



if __name__ == "__main__":

    csv_file = 'doi_files/2018-through-may.csv'
    csv_2017 = 'doi_files/2017.csv'
    bib_file = 'doi_files/my_collection.bib'
    print('do 2018')
    doi_list, numDOIs, numNoDOIs = read_csv(csv_file)
    print('do bib')

    doi_list2, numDOIs2, numNoDOIs2 = read_bib(bib_file)
    print('do 2017')

    doi_list3, numDOIs3, numNoDOIs3 = read_csv(csv_2017)
    print('numDOIs: %d numNoDOIS %d' % (numDOIs3, numNoDOIs3))

    doi_list = [*doi_list, *doi_list2, *doi_list3]

    write_dois_to_file('doi_files/dois.dat', doi_list)

