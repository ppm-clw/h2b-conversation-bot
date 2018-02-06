#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import json,urllib.request,urllib.parse,configparser
from flask import Flask, request, jsonify

app = Flask(__name__)
#日本語文字化け対応
app.config['JSON_AS_ASCII'] = False

# root
# HelloWorld
@app.route('/', methods=['GET'])
def index():
    return 'Hello World'

# GET通信
# 固定のJSONファイルを返却するケース
@app.route('/h2b/test', methods=['GET'])
def get_test_controller():
    # get request data form dialogflow post body
    req = request.get_json(silent=True, force=True)
    # log
    print("Request:")
    print(json.dumps(req, indent=4))
    # read response json file (test)
    res = read_model()
    # make response json and return
    return make_webfook_result(res)

# 固定のJSONファイル読み込み
def read_model():
    try:
        with open('response.json', 'r') as f:
            return json.load(f)
    except IOError as e:
        print(e)
        return None

# GET通信
# 会話テスト（A3RT使用）
@app.route('/h2b/conv/test', methods=['POST'])
def get_test_a3rt():
    # DialogFlowからの受信時のBody
    # 会話の一部を抽出して動的に検索等をする場合はこのデータを使う
    req = request.get_json(silent=True, force=True)
    req = json.dumps(req, indent=4)
    req_json = json.loads(req)

    # ログ
    print("Request:")
    print(req)
    print(req_json)

    # DialogFlowから来た会話文を取得する
    query = req_json['result']['resolvedQuery']

    # Requestオブジェクトにmetho,headersは指定できない。。。
    #method = "POST"
    #headers = {"Content-type": "application/json"}

    # A3RT-smalltaklのURL
    url = "https://api.a3rt.recruit-tech.co.jp/talk/v1/smalltalk"
    # リクエスト用データ作成
    data = make_json_param()
    data["query"] = query

    # 送信するJSONデータをUTF-8でエンコードする
    data = urllib.parse.urlencode(data).encode("utf-8")
    # Requestオブジェクト作成
    req = urllib.request.Request(url, data)
    # POST送信
    with urllib.request.urlopen(req) as res:
        res_json = res.read().decode('utf-8')
        print(res_json)
    # JOSN形式のデコード（※これしないと文字化けます）
    res_json = json.loads(res_json)
    # 返答文言をJSONから取得する
    for results in res_json['results']:
        reply = results['reply']
        print("reply: " + reply)
    # 会話文を含む返却用のJSONを作成
    res_json = create_res_json(reply,reply)
    return make_webfook_result(res_json)


# 外部通信時のリクエストパラメータ取得
# ※固定のURLパラメータは外部ファイルから読み込み
def make_json_param():
    inifile = configparser.ConfigParser()
    inifile.read('./config.ini', 'UTF-8')
    api_key = inifile.get('settings', 'api_key')
    p = {"apikey": api_key}
    return p

# 会話文の作成
def make_speech_sentence(item_name):
    return "現在のランキング一番の商品は、" + item_name + " です。"

# 回答用のJSON作成
def create_res_json(speech, name):
    d = {"speech": speech,"displayText": name,"source": "dialogflow-h2b"}
    return d

# DialogFlowへの返却
def make_webfook_result(data):
    return jsonify(data)


# Main
if __name__ == '__main__':
    app.run(debug=True)
