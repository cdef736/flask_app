import requests
import json
import random
import math
import time
import datetime
import sqlite3

dbname = 'TEST1.db'
conn = sqlite3.connect(dbname)
cur = conn.cursor()
#splited_dat_number[1]はdatの数字print(splited_dat_number[1])
#thread_from_json["threads"][i][2]はサーバー名print(thread_from_json["threads"][i][2])
#splited_dat_number[0]は板の名前print(splited_dat_number[0])

cons ="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
site =requests.get("https://itest.5ch.net/subbacks/poverty.json")
thread_from_json=json.loads(site.text)

thread_url_list=[]
for i in range(int(thread_from_json["total_count"])):
    
    splited_dat_number=thread_from_json["threads"][i][3].split("/")
    
    rand=""
    for i in range(0,10):
     a=cons[math.floor(random.random()*59)]
     rand += a
    print("rand=" + rand)
    thread_url="https://itest.5ch.net/public/newapi/client.php?subdomain=greta&board=poverty&dat=" + splited_dat_number[1] +"&rand=" + rand
    thread_url_list.append(thread_url)
print(len(thread_url_list))
print(thread_url_list)
response_all=[]
array_err=["エラー一覧"]
for o in range(len(thread_url_list)):
    print(f'残り{int(len(thread_url_list))-int(o)}このスレを取得')
    time.sleep(math.floor(random.random()*4))
    print(thread_url_list[o])
    
    get_thread=requests.get(thread_url_list[o])
    try:
     text_from_json=json.loads(get_thread.text)
     for t in range(int(text_from_json["total_count"])):
      print(text_from_json["comments"][t][0])
      print(text_from_json["comments"][t][1])
      print(text_from_json["comments"][t][2])
      print(text_from_json["comments"][t][3])
      print(text_from_json["comments"][t][4])
      print(text_from_json["comments"][t][6])
      print(text_from_json["thread"][5])
      cur.execute('INSERT INTO persons values(?,?,?,?,?,?,?,?)',[text_from_json["thread"][5],text_from_json["comments"][t][1],text_from_json["comments"][t][0],text_from_json["comments"][t][1],text_from_json["comments"][t][2],text_from_json["comments"][t][3],text_from_json["comments"][t][4],text_from_json["comments"][t][6]])
      test={'thread':text_from_json["thread"][5],'thread_id':text_from_json["thread"][0],'number':text_from_json["comments"][t][0],'name':text_from_json["comments"][t][1],'email':text_from_json["comments"][t][2],
    'date':text_from_json["comments"][t][3],'id':text_from_json["comments"][t][4],'text':text_from_json["comments"][t][6]}
      response_all.append(test)
    except:
     array_err.append(thread_url_list[o])


conn.commit()
conn.close()
dt_now = datetime.datetime.now()
f2 =open(f"{dt_now.month}月{dt_now.day}日{dt_now.hour}時{dt_now.minute}{dt_now.second}.json",'w',errors='replace')
json.dump(response_all,f2,indent=2,ensure_ascii=False)
print(len(thread_url_list))
for z in array_err:
    print(z)

