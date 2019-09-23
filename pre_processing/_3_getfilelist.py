import numpy as np
import os, re, nltk, wordninja, operator
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import WordPunctTokenizer
from functools import reduce


in_ROOT = "new-data/"
out_ROOT = "Data4Model/"


def getTag(word):
    tag=[t[-1] for t in nltk.pos_tag(word,tagset='universal')]
    for i in range(len(tag)):
        if tag[i].lower()[0]=='n':  tag[i]='n'
        elif tag[i].lower()[0]=='v':    tag[i]='v'
        elif tag[i]=='ADJ': tag[i]='a'
        elif tag[i]=='ADV': tag[i]='r'
        else: tag[i]='n'
    return tag

def tokenizer(sentence, english_stopwords, ifTrans=True):
    ''' delete network address '''
    http_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')  # 匹配模式
    sentence = http_pattern.sub(" ", sentence)
    http_res_pattern = re.compile(r'http[s]?[:]?[/]?[/]?…')
    sentence = http_res_pattern.sub(" ", sentence)

    ''' delete emoji symbols '''
    try:
        emoji_pattern = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        emoji_pattern = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    sentence = emoji_pattern.sub(" ", sentence)
    emoji_pattern = re.compile(
        u"(\ud83d[\ude00-\ude4f])|"  # emoticons
        u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
        u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
        u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
        u"(\ud83c[\udde0-\uddff])"  # flags (iOS)
        "+", flags=re.UNICODE)
    sentence = emoji_pattern.sub(" ", sentence)

    ''' delete RT... and @... '''
    rt_pattern = re.compile("(?i)rt "); sentence=rt_pattern.sub(" ",sentence)
    rt_pattern= re.compile("@([a-zA-Z]|[0-9])+:*"); sentence = rt_pattern.sub(" ", sentence)
    rt_pattern = re.compile("&([a-zA-Z])+;+"); sentence = rt_pattern.sub(" ", sentence)

    ''' translate a minority language into English '''
    zh_pattern, fr_pattern, ru_pattern = u'[\u4e00-\u9fff]+', u'[\u00C0-\u00FF]+', u'[\u0400-\u052f]+'
    if len(re.findall(zh_pattern, sentence))>0 and ifTrans: return ('zh', sentence)
    elif len(re.findall(fr_pattern, sentence))>0 and ifTrans: return ('fr',sentence)
    elif len(re.findall(ru_pattern, sentence))>0 and ifTrans: return ('ru', sentence)
    elif (len(re.findall(zh_pattern, sentence))>0 or len(re.findall(fr_pattern, sentence))>0 or len(re.findall(ru_pattern, sentence))>0) and ifTrans==False:
        return ("en", "")

    ''' delete punctuation marks that follow the word '''
    sym_pattern=re.compile("\s[^a-zA-Z0-9]+\s")
    sentence = sym_pattern.sub(" ", sentence)

    ''' tokenize '''
    word_token = nltk.word_tokenize(sentence.strip())   # word_token = WordPunctTokenizer().tokenize(sentence.strip())

    ''' delete punctuation marks that is alone '''
    Punc = re.compile("\W+"); abb = re.compile("[\'\_]\w+")
    word_noPunc = [re.sub(Punc, "", w) for w in word_token if Punc.sub("", w) != "" and abb.sub("", w) != ""]
    if len(word_noPunc) < 8: return ('en', "")

    ''' split conjunctions '''
    word_noLong = reduce(operator.add, [[w] if len(wordnet.synsets(w)) else wordninja.split(w) for w in word_noPunc])
    word_noLong = [re.sub(Punc, "", w) for w in word_noLong if Punc.sub("", w) != "" and abb.sub("", w) != ""]

    ''' delete stop-words via NLTK '''
    word_noStop=[w for w in word_noLong if w.lower() not in english_stopwords and w.upper() not in english_stopwords]

    ''' lower case '''
    word_lower = [w.lower() for w in word_noStop]

    ''' lemmatizer '''
    wordnet_lemmatizer = WordNetLemmatizer()
    tag = getTag(word_lower)
    word_lem = [wordnet_lemmatizer.lemmatize(w, tag[i]) for i, w in enumerate(word_lower)]
    return ("en", " ".join(word_lem))



def get_MAX(list_,word_list,topK):
    ind_list = list(np.array(list_).argsort())
    ind_list.reverse()
    ind_list = ind_list[:int(topK)]
    word_=[word_list[x] for x in ind_list]
    return word_



if __name__ =='__main__' :
    with open("stoplist-en.txt", 'r') as file:
        english_stopwords =[str(word).strip("\n").strip() for word in file.readlines()]
    data_dict_2016 = np.load(in_ROOT + 'data_dict_2016.npy').item(0)
    data_dict_2018 = np.load(in_ROOT + 'data_dict_2018.npy').item(0)
    name_dict_2016 = np.load(in_ROOT + 'name_dict_2016.npy').item(0)
    name_dict_2018 = np.load(in_ROOT + 'name_dict_2018.npy').item(0)
    data_dict_list=[data_dict_2016,data_dict_2018]
    name_dict_list=[name_dict_2016,name_dict_2018]

    file_name_list = set([])
    if not os.path.exists(out_ROOT):
        os.makedirs(out_ROOT)

    for i, data_dict in enumerate(data_dict_list):
        name_dict = name_dict_list[i]
        for uid in sorted(list(data_dict.keys())):
            file_name = str(name_dict[uid]) + ".txt"
            file_name_list.add(file_name)
            data_list = []
            for tid in sorted(list(data_dict[uid].keys())):
                (flag, data_tokenize) = tokenizer(data_dict[uid][tid], english_stopwords)
                if flag == "en" and len(data_tokenize) >= 4: data_list.append(data_tokenize)
            data_string = "\n".join(data_list)
            with open(out_ROOT + file_name, "w", encoding="UTF-8") as f:
                f.write(data_string)

    file_name_string = "\n".join(file_name_list)
    with open("filelist.txt", "w") as f:
        f.write(file_name_string)
