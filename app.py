from flask import Flask
from flask import render_template,redirect,url_for
from apscheduler.schedulers.background import BackgroundScheduler
from flask_security import Security, current_user, auth_required, hash_password, \
     SQLAlchemySessionUserDatastore, permissions_accepted,logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from datetime import datetime
import pytz
from sqlalchemy import create_engine,inspect,column
import math
import random
import requests
import json

cons ="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'super-secret'
app.config['SECURITY_PASSWORD_SALT']='my_super_secret_salt'
app.config['SECURITY_POST_LOGOUT_VIEW']='/test_admin'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean())
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False)
    roles = db.relationship('Role',secondary='roles_users',backref=db.backref('users',lazy='dynamic'))

class Role(db.Model,RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)
            
user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
security=Security(app,user_datastore)

def create_model_class(table_name):
        # ダミーのクラスを作成
        class Dummy_Model(db.Model):
            __tablename__ = table_name
            id = db.Column(db.Integer,primary_key=True,unique=True,autoincrement=True)
            thread_name=db.Column(db.Text)
            res_num=db.Column(db.Integer())
            name = db.Column(db.Text)
            res_email=db.Column(db.Text)
            res_time=db.Column(db.String(30))
            user_id = db.Column(db.Text)
            res_text=db.Column(db.Text)
            __table_args__ = {'extend_existing': True}

            
        return Dummy_Model

def to_add_data(table_name):
    class Dummy_Model_2(db.Model):
            __tablename__ = table_name
            id = db.Column(db.Integer,primary_key=True,unique=True,autoincrement=True)
            thread_name=db.Column(db.Text)
            res_num=db.Column(db.Integer())
            name = db.Column(db.Text)
            res_email=db.Column(db.Text)
            res_time=db.Column(db.String(30))
            user_id = db.Column(db.Text)
            res_text=db.Column(db.Text)
    return Dummy_Model_2

list_class_day={}

#ダミーインスタンスを作成して、dictに入れる
def create_dummy_inst(exist_table_array):
    for i in exist_table_array[:-3]:
        list_class_day[i]=to_add_data(i)

# 新しいユーザーを作成
with app.app_context():
        inspector=inspect(db.engine)
        existing_tables=inspector.get_table_names()
        create_dummy_inst(existing_tables)
        db.create_all()
        existing_user = User.query.filter_by(email='matt@test.com').first()
        if not existing_user:
             user_datastore.create_user(email='matt@test.com',password=hash_password('takoye12'))
        db.session.commit()
        db.reflect()





#テーブルを追加する。
#今日の日付を取得し、それに基づくtableが発見されなかった場合に新しいテーブルを作る
def add_table():
     with app.app_context():
        #時間
        japan_tz = pytz.timezone('Asia/Tokyo')
        today = datetime.now(japan_tz)
        month_date = today.strftime("%m%d")
        #month_date = today.strftime("%m%d") これは月と日


        #tableの発見
        inspector=inspect(db.engine)
        existing_tables=inspector.get_table_names()
        table_exists =month_date in existing_tables

        print(table_exists)
        print(existing_tables)

        if not table_exists: 
            print('tableはなし')    
            table_wo_add=create_model_class(month_date)
            list_class_day[month_date]=table_wo_add
            db.create_all()
            print("tableの追加")
            
        #add_clumn_test=testAAA[formatted_date](data="test")
        #db.session.add(add_clumn_test)
        
        
        print("テストモデルの追加に成功")
        db.session.commit()

#各書き込みの日付ごとに格納するtableを分ける
def add_data(thread_title,num,name,mail,date,id,res,date_replaced):
     with app.app_context():
        japan_tz = pytz.timezone('Asia/Tokyo')
        today = datetime.now(japan_tz)
        month_date = today.strftime("%m%d")
        try:
             dummy_class=list_class_day[date_replaced]
        except:
             add_table()
             dummy_class=list_class_day[date_replaced]
        if dummy_class:
            test_data={"thread_name":thread_title,
                       "res_num":num,
                       "name":name,
                       "res_email":mail,
                       "res_time":date,
                       "user_id":id,
                       "res_text":res}
            one_way_inst = dummy_class(**test_data)            
            db.session.add(one_way_inst)
            db.session.commit()


def create_all_test():
     with app.app_context():
          db.create_all()


def scrape_pov(thread_url):
    site =requests.get(thread_url)
    try:
         text_from_json=json.loads(site.text)
         for t in range(int(text_from_json["total_count"])):

            num=text_from_json["comments"][t][0]#number
            name=(text_from_json["comments"][t][1])#name
            mail=(text_from_json["comments"][t][2])#メール
            date=(text_from_json["comments"][t][3])#日時
            date_replaced=date.replace("/","")[4:8]
            id=(text_from_json["comments"][t][4])#id
            res=(text_from_json["comments"][t][6])#レス
            thread_title=(text_from_json["thread"][5])
            print(f"{num}\n{name}\n{mail}\n{date}\n{date_replaced}\n{id}\n{res}\n{thread_title}")
            add_data(thread_title,num,name,mail,date,id,res,date_replaced)
    except Exception as e:
            print(e)

            print("miss")
         
     

def snatch_url():
    rand = [cons[math.floor(random.random()*59)] for _ in range(0,10)]
    rand="".join(rand)
    thread_url=f'https://itest.5ch.net/public/newapi/client.php?subdomain=greta&board=poverty&dat=1701802049&rand={rand}'
    print(thread_url)
    scrape_pov(thread_url)

#スケジューラーの作成
add_table_sche=BackgroundScheduler()
add_table_sche.add_job(add_table,'interval',seconds=10)

@app.route('/')
def root():
     return 'test'

@app.route('/add_test')
def add_to_database():
    return "Test added successfully!"

@app.route('/db_test')
def db_test():
     return render_template("index.html")


@app.route('/test_admin')
@auth_required()
def test_admin():
    user_info = f'User: {current_user.email}' if current_user.is_authenticated else "Not logged in"
    return render_template("index.html")

@app.route('/logout')
@auth_required()
def logout():
     logout_user()

     

#tableの操作系

@app.route('/test_admin/<name>')
def test_admin1(name=None):
    if not add_table_sche.running and name=="start":
         add_table_sche.start()
         print("スケジューラーの起動")
    if add_table_sche.running and name=="shutdown":
         add_table_sche.shutdown()
         print("スケジューラの停止")
    return redirect(url_for('test_admin'))


@app.route('/add_table')
def admin_dashboard():
    add_table()
    return redirect(url_for('test_admin'))

@app.route('/create_all')
def create_table():
     create_all_test()
     return "aaa"

#カラムにデータを追加する系統
@app.route('/add_data')
def add_data_to_table():
     print(list_class_day)
     add_data()

     return redirect(url_for('test_admin'))

@app.route('/add_pov')
def add_poverty():
     snatch_url()
     return "testsucces"


#取得する系統read
@app.route('/get_data/<date>/<name>')
def get_data(date,name="安倍"):
    result=db.session.query(list_class_day[date]).filter(list_class_day[date].name.like(f'%{name}%')).all()
    print(result[1])
    print(dir(result[1]))
    print(result[1].id)
    print(result[0].res_text)
    return "ae"

if __name__=='__main__':
    print("test")
    app.run()
    