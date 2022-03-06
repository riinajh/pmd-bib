'''
    Takes the raw xml.gz files downloaded from baseline by the webscraper and
    filters them based on keyword search, then dumps new compressed files
    into a separate directory.
'''
import os
import copy
import xml.etree.ElementTree as ET
import pickle
import bz2
import gzip
os.chdir(r'C:\path\to\filtered\papers\directory')


def YieldEntries(root, dicttemplate):
    for article in root.iter('PubmedArticle'):
        entry=copy.deepcopy(dicttemplate)
        for title in article.iter('ArticleTitle'):
            name=title.text
            #print(name)
            entry['title']=name
        #Can find an instance of something. looking for one thing though, don't think
        #it can find multiples. also have to double check that its searching only one article
        for author in article.iter('Author'):
            affiliations=[]
            for ln in author.iter('LastName'):
                lastname=ln.text
            try:
                testln=(lastname)
            except UnboundLocalError:
                lastname='n/a'    
            for fn in author.iter('ForeName'):
                forename=fn.text
            try:
                testfn=(forename)
            except UnboundLocalError:
                forename='n/a'
            for affil in author.iter('Affiliation'):
                affiliations.append(affil.text)
            auth=(lastname,forename,affiliations)
            entry['authors'].append(auth)
        #OK! now it can find things with multiple terms and put them into one tuple
        for journal in article.iter('Journal'):
            try:
                ISO=journal.find('.//ISOAbbreviation').text
                entry['journal']=ISO
                #print(ISO)
            except AttributeError:
                ISO='n/a'
                #print(ISO)
            #this one was easy
            try:
                year=journal.find('.//Year').text
            except AttributeError:
                year='n/a'
            try:
                month=journal.find('.//Month').text
            except AttributeError:
                month='n/a'
            try:
                day=journal.find('.//Day').text
            except AttributeError:
                day='n/a'
            #print(year,month,day)
            entry['date']=(year,month,day)
            #apparently some things dont have days or even months associated w their pub dates
            #this makes things a little more annoying.
        for abstract in article.iter('Abstract'):
            abst=[]
            for section in abstract.iter('AbstractText'):
                abst.append(section.text)
                #print(abs)
            entry['abstract']=abst
        # 'no abstract provided' BOI YOU BETTER NOT
        for citation in article.iter('ArticleId'):
            #print(citation.text)
            entry['citations'].append(citation.text)
            #print(entry['citations'])
        for ID in article.iter('PMID'):
            entry['PMID']=(ID.text)
        yield entry



# ok so how are we to filter?
journalkeywords=['Metab','Eng','Synth','Syst']
def journalfilter(index,journalkeywords,relevant_journals, irrelevant_journals):
    '''
        manual review of journal titles that match keywords. auto-includes all
        papers from the selected 'relevant' journals in the final list of papers.
        Returns a list of journals specified to be interesting.
    '''
    for keyw in journalkeywords:
        for entry in index:
            if keyw in entry['journal'] and entry['journal'] not in irrelevant_journals and entry['journal'] not in relevant_journals:
                print(entry['journal'])
                prompt=input('Accept Journal? [y/n] ')
                if prompt == 'y':
                    relevant_journals.add(entry['journal'])
                if prompt == 'n':
                    irrelevant_journals.add(entry['journal'])
    return relevant_journals

abskeywords=['metaboli','edit','synthetic','system','engineer','gene regulat']
antikeywords=['patient','cancer','Cancer','tumor','clinic','obes','neuro','cardio',
              'inflamm','syndrome','Mediterr','person','COVID','anatom','insulin',
              'pharma','Iran','veterinar','dental','child','athlet','sport','surgery',
              'Africa','estrogen','medic','speech','spine','bovine','mouse','osteo','Rat']
            # these commonly co-occur with the keywords of interest so i've 
            # blacklisted them here
def titlefilter(index,abskeywords,antikeywords):
    '''
    

    Parameters
    ----------
    index : List of each article in a particular archive, processed from raw xml by YieldEntries
    abskeywords : Keywords of interest
    antikeywords : keywords to throw out

    Returns
    -------
    relevant : List of papers with titles that suggest interesting content

    '''
    relevant=[]
    for entry in index:
        for keyw in abskeywords:
            try:
                if keyw in str(entry['title']) and entry['title'] not in relevant:
                    if any(antik in str(entry['title']) for antik in antikeywords):
                        continue
                    else:
                        print(entry['title'])
                        relevant.append(entry)
            except:
                continue
    return relevant

abskeywords=['metaboli','edit','synthetic','system','engineer','gene regulat']
antikeywords=['patient','cancer','Cancer','tumor','clinic','obes','neuro','cardio',
              'inflamm','syndrome','Mediterr','person','COVID','anatom','insulin',
              'pharma','Iran','veterinar','dental','child','athlet','sport','surgery',
              'Africa','estrogen','medic','speech','spine','bovine','mouse','osteo','rat']

def abstractfilter(index,abskeywords,antikeywords):
    """
    

    Parameters
    ----------
    index : List of each article in a particular archive, processed from raw xml by YieldEntries
    abskeywords : Keywords of interest
    antikeywords : keywords to throw out

    Returns
    -------
    relevant : List of papers from index that have keywords of interest in their abstracts

    """
    
    relevant=[]
    for entry in index:
        for keyw in abskeywords:
            try:
                if keyw in str(entry['abstract']):
                    if any(antik in str(entry['abstract']) for antik in antikeywords):
                        continue
                    else:
                        print(entry['title'])
                        relevant.append(entry)
            except:
                continue
    return relevant

dicttemplate={'authors':[],'date':[],'title':'','journal':'','abstract':'','citations':[],'PMID':''}
relevant_journals=set()
irrelevant_journals=set()
for file in os.scandir(r'C:\path\to\downloaded\archives\directory'):
    f = gzip.open(file, 'rb')
    file_content = f.read().decode()
    f.close()
    articleset=ET.fromstring(file_content)
   # this is actually an elementtree root element, not a tree itself. i think everything
   # still works though
    index=[]
    for article in YieldEntries(articleset,dicttemplate):
        index.append(article)
    relevants=[]
    morerelevants=titlefilter(index,abskeywords,antikeywords)
    for moreentries in morerelevants:
        if moreentries not in relevants:
            relevants.append(moreentries)
    evenmorerelevants=abstractfilter(index,abskeywords,antikeywords)
    for evenmoreentries in evenmorerelevants:
        if evenmoreentries not in relevants:
            relevants.append(evenmoreentries)
    # relevantjournals=journalfilter(index,journalkeywords,relevant_journals,irrelevant_journals)
    # for entry in index:
    #     for journal in relevantjournals:
    #         if entry['journal'] == journal:
    #             #print(entry['title'])
    #             relevants.append(entry)
    #the journal title filter just ended up being to much stuff to sift through. 
    pubmedentries=bz2.BZ2File('Index '+ str(file)[11:24], 'w')
    pickle.dump(relevants,pubmedentries)
    pubmedentries.close()
    #this bit here will dump compressed, filtered archives into whatever directory
    #was cd'd at the top