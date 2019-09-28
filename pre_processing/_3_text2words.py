import numpy as np
import os, re, nltk, wordninja, operator
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import WordPunctTokenizer
from functools import reduce
from stanfordcorenlp import StanfordCoreNLP
nlp = StanfordCoreNLP(r'D:\Python\Python36\stanford-corenlp-full-2018-10-05')



in_ROOT = "new-data/"
out_ROOT = "Data4Model/"


''' delete network address '''
def rmHttp(sentence):
    http_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')  # 匹配模式
    sentence = http_pattern.sub(" ", sentence)
    http_res_pattern = re.compile(r'http[s]?[:]?[/]?[/]?…')
    sentence = http_res_pattern.sub(" ", sentence)
    return sentence

''' delete emoji symbols '''
def rmEmoji(sentence):
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
    return sentence


''' delete RT... and @... '''
def rmRT(sentence):
    rt_pattern = re.compile("(?i)rt ")
    sentence = rt_pattern.sub(" ", sentence)
    rt_pattern = re.compile("@([a-zA-Z]|[0-9])+:*")
    sentence = rt_pattern.sub(" ", sentence)
    rt_pattern = re.compile("&([a-zA-Z])+;+")
    sentence = rt_pattern.sub(" ", sentence)
    return sentence


''' translate a minority language into English '''
def judLanguage(sentence):
    zh_pattern, fr_pattern, ru_pattern = u'[\u4e00-\u9fff]+', u'[\u00C0-\u00FF]+', u'[\u0400-\u052f]+'
    if len(re.findall(zh_pattern, sentence)) > 0 and ifTrans:
        return ('zh', sentence)
    elif len(re.findall(fr_pattern, sentence)) > 0 and ifTrans:
        return ('fr', sentence)
    elif len(re.findall(ru_pattern, sentence)) > 0 and ifTrans:
        return ('ru', sentence)
    elif (len(re.findall(zh_pattern, sentence)) > 0 or len(re.findall(fr_pattern, sentence)) > 0 or len(re.findall(ru_pattern, sentence)) > 0) and ifTrans == False:
        return ("en", "")
    else:
        return ("en", sentence)


def getTag(sent):
    pos_tag, new_tag = [w[-1] for w in nlp.pos_tag(sent)], []       # Enter a sentence
    # pos_tag, new_tag = [nlp.pos_tag(w)[0][-1] for w in word], []  # Enter a word list
    # pos_tag, new_tag = [t[-1] for t in nltk.pos_tag(word)], []    # NLTK is inaccurate
    for i, tag in enumerate(pos_tag):
        if str(tag).startswith("NN"): new_tag.append("n")       # Nouns(plural), Proper Nouns(plural)
        elif str(tag).startswith("VB"): new_tag.append("v")     # Verb
        elif str(tag).startswith("JJ"): new_tag.append("a")     # Adjective (comparative, supreme)
        elif str(tag).startswith("R"): new_tag.append("r")      # Adverbs (comparative, supreme)
        else: new_tag.append("n")
    return new_tag


def tokenizer(sentence, english_stopwords):
    ''' delete network address '''
    sentence = rmHttp(sentence)
    ''' delete emoji symbols '''
    sentence = rmEmoji(sentence)
    ''' delete RT... and @... '''
    sentence = rmRT(sentence)
    # ''' translate a minority language into English '''
    # (flag, sentence) = judLanguage(sentence)
    # if flag != "en" or len(sentence) <= 0: return (flag, sentence)

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
    word_noStop = [w.lower() for w in word_noLong if w.lower() not in english_stopwords and w.upper() not in english_stopwords]

    ''' lemmatizer '''
    tag = getTag(" ".join(word_noStop))
    wordnet_lemmatizer = WordNetLemmatizer()
    word_lem = [wordnet_lemmatizer.lemmatize(w, tag[i]) for i, w in enumerate(word_noStop)]

    return ("en", " ".join(word_lem))



if __name__ =='__main__' :
    english_stopword = []
    with open("stoplist-en.txt", 'r') as file:
        english_stopwords =[str(word).strip("\n").strip() for word in file.readlines()]

    data_dict_2016 = np.load(in_ROOT + 'data_dict_2016.npy').item(0)
    data_dict_2018 = np.load(in_ROOT + 'data_dict_2018.npy').item(0)
    data_dict_russian = np.load(in_ROOT + "data_dict_russian.npy").item(0)
    data_dict_list=[data_dict_2016,data_dict_2018,data_dict_russian]
    plus = [201600000, 201800000, 0]

    file_name_list = set([])
    if not os.path.exists(out_ROOT):
        os.makedirs(out_ROOT)

    for i, data_dict in enumerate(data_dict_list):
        for uid in sorted(list(data_dict.keys())):
            file_name = str(int(uid)+plus[i]) + ".txt"
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
