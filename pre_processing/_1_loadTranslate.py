import csv, time, numpy, random, json, re
import preproccess.B3_getfilelist as prep
from urllib import request, parse


ip = "117.191.11.110:8080"
Request_URL = "http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule"
form_data = {}
form_data['i'] = "hello"
form_data['from'] = 'AUTO'
form_data['to'] = 'AUTO'
form_data['smartresult'] = 'dict'
form_data['doctype'] = 'json'
form_data['version'] = '2.1'
form_data['keyfrom'] = 'fanyi.web'
form_data['action'] = 'FY_BY_CLICKBUTTION'
form_data['typoResult'] = 'false'

proxies_list=['39.137.77.68:80','125.129.52.135:8197','116.196.91.182:3128','112.87.69.27:9999','112.85.165.220:9999']

handler_list=['Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0',
              "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36",
              'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
              'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
              'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11']



def translate(loc, sentence):
    global proxies_list, ip
    ERR, maxCount, translate_res = True, 10, ""
    while ERR and maxCount > 0:
        proxies, handler = {"http": ip}, [('User-Agent',random.choice(handler_list) )]
        proxy_support = request.ProxyHandler(proxies)
        opener = request.build_opener(proxy_support)
        opener.add_handler = handler
        request.install_opener(opener)
        try:
            form_data['i'], form_data['from'], form_data['to'] = sentence, loc, 'AUTO'
            data = parse.urlencode(form_data).encode('utf-8')
            response = request.urlopen(Request_URL, data,timeout=5)
            html = response.read().decode('utf-8')
            translate_results = json.loads(html)
            translate_res = translate_results["translateResult"][0][0]['tgt']
            print(loc,"->",'AUTO',translate_res)
        except:
            print(ip,"is error")
            if ip in proxies_list:
                ind = proxies_list.index(ip)
                proxies_list.pop(ind)
            if len(proxies_list) < 20:
                with open("download.txt", 'r') as file:
                    lines = file.readlines()
                    proxies_list = [l.strip("\n").strip() for l in lines]
            ip = random.choice(proxies_list)
            maxCount-=1
        else:
            ERR=False
    if maxCount <= 0:
        return sentence
    try:
        form_data['i'], form_data['from'], form_data['to'] = translate_res, 'AUTO', 'en'
        data = parse.urlencode(form_data).encode('utf-8')
        response = request.urlopen(Request_URL, data,timeout=5)
        html = response.read().decode('utf-8')
        translate_results = json.loads(html)
        translate_en = translate_results["translateResult"][0][0]['tgt']
        print("AUTO","->",'en',translate_en)
        return translate_en
    except:
        return sentence



''' translate a minority language into English '''
def judLanguage(sentence):
    zh_pattern, fr_pattern, ru_pattern = u'[\u4e00-\u9fff]+', u'[\u00C0-\u00FF]+', u'[\u0400-\u052f]+'
    if len(re.findall(zh_pattern, sentence)) > 0:
        return ('zh', sentence)
    elif len(re.findall(fr_pattern, sentence)) > 0:
        return ('fr', sentence)
    elif len(re.findall(ru_pattern, sentence)) > 0:
        return ('ru', sentence)
    else:
        return ("en", sentence)



if __name__ =='__main__' :
    haveTrans_dict = numpy.load("haveTrans_dict.npy").item(0)
    csv_file = csv.reader(open('tweets.csv', 'r', encoding='UTF-8'))
    nameDict, user_time_data_dict, minCount = {}, {}, 10000
    for i,line in enumerate(csv_file):
        user_name, tweet, timestr = line[1], str(line[11]).strip(" "), line[12]
        try:
            timeArray = time.strptime(timestr, "%Y-%m-%d %H:%M")
            timeStamp = int(time.mktime(timeArray))
        except:
            continue
        else:
            ''' if loc is not english or we cannot translate it '''
            (loc, sentence) = judLanguage(tweet)
            if loc != 'en' and len(sentence) > 0:
                if sentence in list(haveTrans_dict.keys()):
                    tweet = haveTrans_dict[sentence]
                else:
                    tweet = translate(loc, sentence)
                    if tweet == sentence: continue
                    else: haveTrans_dict[sentence] = tweet; numpy.save("haveTrans_dict.npy", haveTrans_dict)

            ''' add or upgrade the data of user_name '''
            if user_name not in nameDict.keys():
                nameDict[user_name] = minCount
                minCount += 1
            user_id = nameDict[user_name]
            if user_id not in user_time_data_dict.keys(): user_time_data_dict[user_id] = {}
            if len(tweet) >10: user_time_data_dict[user_id][timeStamp] = tweet
    numpy.save("data_dict.npy", user_time_data_dict)

