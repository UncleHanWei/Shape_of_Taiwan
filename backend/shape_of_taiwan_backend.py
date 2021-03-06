import flask
import logging
from flask import jsonify, request, render_template
import json
from topic_analysis_module import data_preprocess, computer_doc_sims
from getWebText import getWebText

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config["JSON_AS_ASCII"] = False
format_config = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=format_config, level=logging.INFO)
logger = logging.getLogger()

@app.route('/getData', methods=['GET'])
def getData() :
    def get_result_json(webText): # private, 傳進網頁內容，return 比對到 網頁 與 key 的
        # 資料準備
        # content = open('./static/web_content_demo.txt', 'r', encoding='utf8').read() # request - web content
        ch_dict_file = open('./static/data.json','r',encoding='utf8') # zh_CH.json
        ch_json_array = json.load(ch_dict_file)

        # 收到 web 資料後作預處理，return 清除符號、數字、同義字的 str
        words_str = data_preprocess(webText)
        words = words_str.split(' ')
        
        # 取得 doc 的 topic
        if(computer_doc_sims(words_str) >= 0.7):
            topic = 'computer'
        else:
            topic = "N"

        result_json = dict()
        for word in words: # 每個斷詞
            try: 
                print(topic == ch_json_array[word]['topic'])
                if(ch_json_array[word]['topic'] == 'N'):
                    result_json[word] = ch_json_array[word]
                elif(topic == ch_json_array[word]['topic']): # 先確定有無限定 topic
                    result_json[word] = ch_json_array[word] # 比對 ch_json_array[ch_key]
            except KeyError:
                continue

        with open('./static/result_data.json', 'w', encoding='UTF-8') as f:
            f.write(str(json.dumps(result_json, ensure_ascii=False)))
        with open('./static/result_data.json', 'r', encoding='UTF-8') as f:
            return jsonify(json.load(f))

    if 'url' in request.args :
        url = request.args['url']
        # htmlString = get(url).text
        webText = getWebText(url)

    return get_result_json(webText)


@app.route('/feedBack', methods=['GET'])
def feedBack():
    return render_template('test.html')


@app.route('/updateData', methods=['GET'])
def updateData():
    if 'zh_CN' in request.args :
        if request.args['zh_CN'] == '' :
            return "Error: Form format error"
        else :
            key = request.args['zh_CN']
            if 'zh_TW' in request.args and 'en_US' in request.args :
                zh_TW = request.args['zh_TW']
                en_US = request.args['en_US']
            else :
                return "Error: Form format error"
    else :
        return "Error: Form format error"
    data = None
    with open('./static/data.json', 'r', encoding='utf8') as f :
        data = json.load(f)
        data[key] = {
            "zh_TW": zh_TW,
            "en_US": en_US
        }
    with open('./static/data2.json', 'w', encoding='utf8') as f :
        json.dump(data, f, ensure_ascii=False)
    return "Success"

if __name__ == "__main__":
    app.run()