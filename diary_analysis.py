from textblob import TextBlob
from nltk.corpus import stopwords
import os, math
import re
import numpy as np
from datetime import datetime

months = {1:'January', 2:'February', 3:'March', 4:'April', 5:'May', 6:'June', 7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 12:'December'}
base_year = 2012
num_years = 6
start_month = 10
end_month = 9

def get_wf(diary):
    wf = {}
    #  for word in diary.noun_phrases:
    length = len(diary.words)
    for word in diary.words:
        wf[word] = wf[word]+1 if word in wf else 1.0
    for word in wf:
        assert (type(wf[word]) is float)
        wf[word] = (wf[word], round(wf[word]/length*100,5))
    return wf

def verify_clean_data(raw_diary):
    for i in range(num_years):
        for month in months.values():
            month_year = month + ' ' + str(i+base_year)
            if raw_diary.count(month_year) > 1:
                print month_year
                raise ValueError(month_year)

def clean_words(raw_diary):
    diary = TextBlob(raw_diary)
    stop = set(stopwords.words('english'))
    cleaned_diary = []
    for word in diary.words:
        if word.lower() not in stop:
            cleaned_diary.append(re.sub(r'\W+', '', word.lower()).title())
    return TextBlob(' '.join(cleaned_diary))

def write_to_file(filename, contents):
    f = open('output/'+filename, 'w+')
    f.write(contents)

def sort_wf(diary, number, time):
    word_frequency = get_wf(diary)

    sorted_words = sorted(word_frequency.items(), key=lambda x: x[1][1], reverse=True)
    words, scores = zip(*sorted_words[:number])
    csv = ''
    for i, (word, score) in enumerate(sorted_words[:number]):
        tf = score[0]
        percentage = str(score[1]) + '%'
        print "\tIndex: ", i ," Word: ", word, " TF: ", tf, " %: ", percentage
        csv += str(word) + ',' + str(tf) + ',' + percentage + '\n'
    filename = 'wf_' + time + datetime.now().strftime('%Y-%m-%d-%H-%M-%s') + '.csv'
    write_to_file(filename, csv)

def get_month_year(index):
    if index < 3:
        return str(months.get(start_month + index)) + ' ' + str(base_year)
    else:
        remaining = index - 3
        year = 1 + remaining/12 + base_year
        month = months.get(remaining%12+1)
        return str(month) + ' ' + str(year)

def split_by_year(raw_diary):
    diary_by_year = []
    for i in range(1,num_years):
        year = base_year+i-1
        idx = raw_diary.find('January ' + str(year))
        diary_by_year.append( (str(year+1), clean_words(raw_diary[:idx])) )
        raw_diary = raw_diary[idx:]
    diary_by_year.append((str(base_year+num_years-1), clean_words(raw_diary)))
    print('Number of years analyzed: ' + str(len(diary_by_year)))
    assert len(diary_by_year) == num_years
    return diary_by_year

def split_by_month(raw_diary):
    diary_by_month = []
    num_months = (num_years-1)*12 + (end_month-start_month)
    for i in range(1,num_months+1):
        month_year = get_month_year(i-1)
        idx = raw_diary.find(get_month_year(i))
        diary_by_month.append((month_year, clean_words(raw_diary[:idx])))
        raw_diary = raw_diary[idx:]
    diary_by_month.append( (get_month_year(num_months), clean_words(raw_diary)) )
    print('Number of months analyzed: ' + str(len(diary_by_month)))
    return diary_by_month

def analyze_sentiment_all(diary):
    overall_sentiment = diary.sentiment
    polarity = str(overall_sentiment.polarity)
    subjectivity = str(overall_sentiment.subjectivity)
    print('Sentiment Analysis overall: ' + polarity)
    csv = 'Polarity, Subjectivity\n'
    csv += polarity + ',' + subjectivity + '\n'
    filename = 'sentiment_overall' + datetime.now().strftime('%Y-%m-%d-%H-%M-%s') + '.csv'
    write_to_file(filename, csv)
    return overall_sentiment

def analyze_sentiment_list(time, diary_list):
    sentiments = []
    csv = time + ', Polarity, Subjectivity\n'
    filename = 'sentiment_by_' + time + datetime.now().strftime('%Y-%m-%d-%H-%M-%s') + '.csv'
    for diary in diary_list:
        text = diary[1]
        text_id = diary[0]
        sentiment = text.sentiment
        polarity = str(sentiment.polarity)
        subjectivity = str(sentiment.subjectivity)
        print('Sentiment Analysis for ' + text_id + ': ' + polarity)
        csv += text_id + ',' + polarity + ',' + subjectivity + '\n'
        sentiments.append((text_id, polarity, subjectivity))
    write_to_file(filename, csv)
    return sentiments

def analyze_sentiment_month(diary_by_month):
    monthly_sentiments = {}
    for month in months.values():
        monthly_sentiments[month] = (0.0,0)
    csv = 'Month, Polarity\n'
    filename = 'sentiment_by_month_grouped_' + datetime.now().strftime('%Y-%m-%d-%H-%M-%s') + '.csv'
    for diary in diary_by_month:
        month_year = diary[0]
        text = diary[1]
        sentiment = text.sentiment
        polarity = sentiment.polarity
        for month in months.values():
            if month in month_year:
                prev_sentiment = monthly_sentiments[month][0]
                prev_num_months = monthly_sentiments[month][1]
                monthly_sentiments[month] = (prev_sentiment+polarity, prev_num_months+1)
                break
    monthly_sentiments_aggregated = {}
    for k in monthly_sentiments.keys():
        sentiment = monthly_sentiments[k]
        polarity = sentiment[0]/sentiment[1]
        print 'Month: ', k, ' Polarity: ', str(polarity)
        csv += k + ',' + str(polarity) + '\n'
        monthly_sentiments_aggregated[k] = polarity
    write_to_file(filename, csv)
    return monthly_sentiments_aggregated

def get_wf_for_word(word, wfs):
    wf_word = []
    csv = 'Word,Index,TF,%\n'
    filename = 'wf_' + word + datetime.now().strftime('%Y-%m-%d-%H-%M-%s') + '.csv'
    for wf in wfs:
        idx = wf[0]
        text = wf[1]
        tf, percentage = text.get(word, (0, 0.0))
        wf_word.append( (idx, word, tf, percentage) )
        print  'Word: ' + word + ' Index: ' + idx + ' TF: ' + str(tf) + ' %: ' + str(percentage) + '%'
        csv += str(word) + ',' + idx + ',' + str(tf) + ',' + str(percentage) + '%' + '\n'
    write_to_file(filename, csv)
    return wf_word

def get_new_words(wfs):
    new_words = []
    filename = 'wf_new_words' + datetime.now().strftime('%Y-%m-%d-%H-%M-%s')
    contents = ''
    for i in range(1, len(wfs)):
        idx = wfs[i][0]
        prev_wf = wfs[i-1][1]
        current_wf = wfs[i][1]
        word_diff = {}
        for word in current_wf.keys():
            (diff_freq, diff_percentage) = np.subtract(current_wf[word],prev_wf.get(word, (0, 0.0)))
            word_diff[word] = (diff_freq, diff_percentage)
        new_words.append( (idx, sorted(word_diff.items(), key=lambda x: x[1][1], reverse=True)) )
    for nw in new_words:
        print nw[0]
        contents += nw[0] + '\n'
        for (word, score) in nw[1][:10]:
            freq, percentage = score
            percentage = str(percentage) + '%'
            print "\tWord: ", word, " Score: " + str(freq), " Percentage: " + percentage
            contents += "\tWord: " + word + " Score: " + str(freq) + " Percentage: " + percentage + '\n'
        for (word, score) in nw[1][-10:]:
            freq, percentage = score
            percentage = str(percentage) + '%'
            print "\tWord: ", word, " Score: " + str(freq), " Percentage: " + percentage
            contents += "\tWord: " + word + " Score: " + str(freq) + " Percentage: " + percentage + '\n'
        contents += '\n'
    write_to_file(filename, contents)
    return new_words

if __name__ == '__main__':
    with open('/Users/jchang1397/Downloads/diary', 'r') as d:
    #  with open('test', 'r') as d:
        raw_diary = d.read().decode('utf-8')
    verify_clean_data(raw_diary)

    #  diary = clean_words(raw_diary)
    #  analyze_sentiment_all(diary)
    #  sort_wf(diary, 100, 'all')

    #  diary_by_year = split_by_year(raw_diary)
    #  analyze_sentiment_list('Year', diary_by_year)
    #  analyze_sentiment_year(diary_by_year)

    diary_by_month = split_by_month(raw_diary)
    #  analyze_sentiment_list('Month', diary_by_month)
    wf_by_month = []
    for month in diary_by_month:
        text = month[1]
        idx = month[0]
        wf_by_month.append( (idx, get_wf(text)) )
    #  get_wf_for_word('Tired', wf_by_month)
    #  get_wf_for_word('Sad', wf_by_month)
    #  get_wf_for_word('Happy', wf_by_month)
    #  get_wf_for_word('Good', wf_by_month)
    #  get_wf_for_word('Pvns', wf_by_month)
    #  analyze_sentiment_month(diary_by_month)
    new_words = get_new_words(wf_by_month)

