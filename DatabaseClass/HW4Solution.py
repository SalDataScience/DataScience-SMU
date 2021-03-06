"""
DB HW #4 - Fall 2015
Rahn Lieberman

original Source Code from
    http://stackoverflow.com/questions/8286554/find-anagrams-for-a-list-of-words

- Modified:
    Add add a word counter.
    better entry point.
    Add graphing of histograms
    Added SQL portion 
    Code cleanup, etc.
	And a whole bunch more.
	
"""

from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
import sqlite3
import urllib2

#Read word list from a the source file
#For each word, it removes whitespace and junk
# This list is from https://raw.githubusercontent.com/dwyl/english-words/master/words.txt
# has b bit over 350K words
def load_words(filename='d:/words.txt'):
    with open(filename) as f:
        for word in f:
            yield word.rstrip()
    
# Reads word list from URL  
def load_words_FromURL(filename):
    data = urllib2.urlopen(filename).read().split("\n")
    return data
    
# For each word in the loaded words, create a new dictionary entry for it.
# return the dictionary of all words, with the original word as the key, and 
# the value all letters in the word, sorted.
def get_anagrams(source):    
    d = defaultdict(list)
    for word in source:
        key = "".join(sorted(word)).replace("'","")
        d[key].append(word)
    return d

# Go through the dictionary of all words. 
# the dictionary is sorted
# compare the "key" word (word being looked up) to all items 
# in the anagram list.  If they are the same length, then they are an anagram.
def print_anagrams(d):
    counter = 0
    highcount=0
    highcountwords = ""
    
    for key, anagrams in d.iteritems():
        length = len(anagrams)
                
        if length > 1:
            #print(key,anagrams)
            counter += 1
    
            #see if this word has the most anagrams so far.            
            if length > highcount:
                highcount = len(anagrams)
                highcountwords = anagrams
                            
    print "There are ", counter, " anagrams found."
    print "High counter is: ", highcount, highcountwords
    Create_Histogram(d)

# Show a chart of the words
# create a bar chart.  Note the import of numpy and mtlibplot above   
def Create_Histogram(dictionaryWords):
    histogramDict = defaultdict(int)
    for key, anagrams in dictionaryWords.iteritems():  
        if len(anagrams) > 1:
            histogramDict[str(len(anagrams))]+=1 #add count to histogram 
    
    print "The histogram dictionary looks like:"
    print histogramDict.items()

    X = np.arange(len(histogramDict))
    plt.bar(X, histogramDict.values(),align='center', width=0.5)
    plt.xticks(X,histogramDict.keys())
    plt.ylim(0, 7500)
    plt.show()


# Create a SQLite DB if it doesn't exist already and add our table.
def Database_Initializer():
    CreateAnagramTable()
  

#Create our table to hold the anagrams
def CreateAnagramTable():
    c.execute("DROP TABLE IF EXISTS anagrams;") #allows for rerunning :)   
    c.execute("""
    CREATE TABLE anagrams (
    UniqueAnagramID varchar(20) NOT NULL,
    numberWords int NOT NULL,
    WordList varchar(500) NOT NULL) 
    """)
    
    # create the merrian-webster table, needed for last questions
    c.execute("DROP TABLE IF EXISTS mw;") #allows for rerunning :)   
    c.execute("""
    CREATE TABLE mw (
    MWAnagramID varchar(20) NOT NULL,
    numberWords int NOT NULL,
    WordList varchar(500) NOT NULL) 
    """)
        
    conn.commit()


# take a list of values, and insert them all into DB
#  Would be better to pass in a tuple(s) and execute many
#  but it's late and I'm working record by record
def Insert_Anagrams(dict_Anag, tableName):  
    count = 0    
    if tableName=="ospd":
        for key, value in dict_Anag.iteritems():
            ins = "insert into anagrams values ('%s', %d, '%s')" % (key, len(value), str(value).replace("'",""))
            c.execute(ins)
            count +=1
    else: 
        for key, value in dict_Anag.iteritems():
            try:
                if (len(key)>1 and len(value)>1):                
                    ins = "insert into mw values ('%s', %d, '%s')" % (key, len(value), str(value).replace("'",""))
                    c.execute(ins)
                    count +=1
            except Exception, err:
                print err
                print ins

    conn.commit()
    print count, 'words inserted'

  
# just to see whats in there...
def SelectAllFromDB():
    for row in c.execute("select * from anagrams"):
        print row

#  Get number of anagrams with more than 1 word.
# (Question 4)
def GetNumberAnagramsFromOSPDList():
    c.execute("select count(*) from anagrams where numberWords>1")
    print c.fetchone()[0]


def GetHighestAnagramListFromOSPDList():
    c.execute("select * from anagrams order by numberWords Desc limit 1")
    print c.fetchone()

#question 6
def GetNumberAnagramsFromMWList():
    c.execute("select count(*) from mw where numberWords>1")
    print c.fetchone()[0]


def GetHighestAnagramListFromMWList():
    c.execute("select * from mw order by numberWords Desc limit 1")
    print c.fetchone()

def Main():
    #calculate the anagrams and do the stuff for q1-3
    word_source = load_words_FromURL('http://www.puzzlers.org/pub/wordlists/ospd.txt')
    mw_words=load_words_FromURL('https://raw.githubusercontent.com/dwyl/english-words/master/words.txt')
    # Alternate was to pass a word list in. 
    #word_source = ["eat","ate","tea","draper","parred", "stone", "tones", "onset", "tonse","bob","feet"]
    dict_anagrams = get_anagrams(word_source)
    dict_mw = get_anagrams(mw_words)
     
    print_anagrams(dict_anagrams)

    #Q4-6 - DB questions
    Database_Initializer()
    Insert_Anagrams(dict_anagrams,'ospd')
    #SelectAllFromDB()

    print 'Question 4: How many anagrams:'
    GetNumberAnagramsFromOSPDList()
    print 'Question 5: What is largest # of words with anagrams'
    GetHighestAnagramListFromOSPDList()
    
    #repeat for large word set (350k+)
    Insert_Anagrams(dict_mw, 'mw')
    print 'Question 6: How many anagrams:'
    GetNumberAnagramsFromMWList()
    print 'Question 7: What is largest # of words with anagrams'
    GetHighestAnagramListFromMWList()
    
###########################################
# program entry point.
if __name__ == '__main__':
    conn = sqlite3.connect('hw4.db') #make this global
    c = conn.cursor()
    
    Main()
