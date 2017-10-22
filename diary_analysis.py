from textblob import TextBlob
from nltk.corpus import stopwords
import os, math
import re
import matplotlib.pyplot as plt
import numpy as np

months = {1:'January', 2:'February', 3:'March', 4:'April', 5:'May', 6:'June', 7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 12:'December'}
base_year = 2012
start_year = 2
end_year = 7
start_month = 10

def tf(diary):
    wf = {}
    #  for word in diary.noun_phrases:
    for word in diary.words:
        if word in wf:
            wf[word] = wf.get(word)+1
        else:
            wf[word] = 1
    return wf

def verify_clean_data(raw_diary):
    for i in range(start_year, end_year):
        for month in months.values():
            month_year = month + ' 201' + str(i)
            if raw_diary.count(month_year) > 1:
                print month_year
                raise ValueError(month_year)

def clean_words(diary):
    stop = set(stopwords.words('english'))
    cleaned_diary = []
    for word in diary.words:
        if word.lower() not in stop:
            cleaned_diary.append(re.sub(r'\W+', '', word.lower()).title())
    return TextBlob(' '.join(cleaned_diary))

def plot_wf(diary, number):
    word_frequency = tf(diary)

    sorted_words = sorted(word_frequency.items(), key=lambda x: x[1], reverse=True)
    words, scores = zip(*sorted_words[:number])
    for i, (word, score) in enumerate(sorted_words[:number]):
        print "\tIndex: ", i ," Word: ", word, " TF: ", round(score,5), " %: ", float(score)/len(diary.words)
    xpos = np.arange(len(words))
    plt.bar(xpos, scores)
    plt.xticks(xpos, words)
    plt.show()

def split_by_year(diary):
    diary_by_year = []
    for i in range(start_year,end_year):
        idx = diary.find('January 201' + str(i))
        diary_by_year.append(diary[:idx])
        diary = diary[idx:]
    print (len(diary_by_year))
    assert len(diary_by_year) == end_year-start_year+1
    print('Number of years analyzed: ' + str(len(diary_by_year)))
    return diary_by_year

def split_by_month(diary):
    regex = '('
    for month in months.values():
        regex += month + '|'
    regex = regex[:-1]
    regex += ') 201[' + str(start_year) + '-' + str(end_year) + ']'
    print (regex)
    diary_by_month = re.split(regex, diary)
    print('Number of months analyzed: ' + str(len(diary_by_month)))
    return diary_by_month

def analyze_sentiment_overall(diary):
    overall_sentiment = diary.sentiment
    print('Sentiment Analysis overall: ' + str(overall_sentiment.polarity))
    return overall_sentiment

def analyze_sentiment_year(raw_diary):
    years = []
    for i, y in enumerate(diary_by_year):
        year = TextBlob(y)
        idx = i + base_year
        year_sentiment = year.sentiment
        print('Sentiment Analysis for ' + str(idx) + ': ' + str(year_sentiment.polarity))
        years.append((idx, year_sentiment.polarity, year.sentiment.subjectivity))
    return years

def get_month_year(index):
    if index < 3:
        return str(months.get(start_month + index)) + ' ' + str(base_year)
    else:
        remaining = index - 3
        year = 1 + remaining/12 + base_year
        month = months.get(remaining%12+1)
        return str(month) + ' ' + str(year)

def analyze_sentiment_month(raw_diary):
    months = []
    for i, m in enumerate(diary_by_month):
        month = TextBlob(m)
        idx = get_month_year(i)
        month_sentiment = month.sentiment
        print('Sentiment Analysis for ' + str(idx) + ': ' + str(month_sentiment.polarity))
        months.append((idx, month_sentiment.polarity, month.sentiment.subjectivity))
    return months

if __name__ == '__main__':
    #  with open('/Users/jchang1397/Downloads/diary', 'r') as d:
    with open('test', 'r') as d:
        raw_diary = d.read().decode('utf-8')
    verify_clean_data(raw_diary)
    diary = clean_words(TextBlob(raw_diary))

    #  plot_wf(diary, 100)

    #  analyze_sentiment_overall(diary)
    diary_by_year = split_by_year(raw_diary)
    #  analyze_sentiment_year(diary_by_year)
    diary_by_month = split_by_month(raw_diary)
    #  for m in diary_by_month:
        #  print ('\n')
        #  print ('split\n')
        #  print (m)
    print( str(diary_by_month[1]))
    #  analyze_sentiment_month(diary_by_month)

    #  diary_by_month = split_by_month(raw_diary)
