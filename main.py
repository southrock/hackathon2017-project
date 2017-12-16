from flask import Flask,jsonify,session,redirect,url_for,render_template,request
import re,sqlite3,requests,time

app = Flask(__name__)
app.secret_key = 'HOMURACHAN'

def getinformation(token):
    url = 'https://www.ncuos.com/api/user/profile/basic'
    url2 = 'https://www.ncuos.com/api/user/profile/school_roll'
    headers = {'content-type': 'application/json','Authorization':r'passport '+ token} 
    e = requests.get(url,headers=headers)
    i = requests.get(url2,headers=headers)
    rule = re.compile(r"\D(\d\d)")
    nj = rule.findall(i.json()['school_roll'][0]['bjmc'])
    information = {
                'xm':e.json()['base_info']['xm'],
                'xb':e.json()['base_info']['xb']['mc'],
                'xy':i.json()['school_roll'][0]['xy'],
                'nj':nj[0]
    }
    return information

def getcard():
    card = sqlite3.connect('sql/card.db')
    c = card.cursor()
    c.execute('select cardID,fromID,whatsay from card where ((getID = NULL and xylimit = "wu") and fromID <> "%s") limit 1'%session.get('schid'))
    a = c.fetchall()
    c.execute('select cardID from card where ((getID = "%s" and whatsay ="%s") and fromID="%s")'%(session.get('schid'),a[0][2],a[0][1]))
    b = c.fetchall()
    if b:
        if a:
            c.execute('update card set getID = "%s" where cardID = "%s"'%(session.get('schid'),a[0][0]))
            card.commit()
    c.execute('select cardID,fromID from card where ((getID = NULL and xylimit = "%s") and fromID <> "%s") limit 1;'%(session.get('xy'),session.get('schid')))
    a = c.fetchall()
    c.execute('select cardID from card where ((getID = "%s" and whatsay ="%s") and fromID="%s")'%(session.get('schid'),a[0][2],a[0][1]))
    d = c.fetchall()
    if d:
        if a:
            c.execute('update card set getID = "%s" where cardID = "%s"'%(session.get('schid'),a[0][0]))
            card.commit()
            card.close()

@app.route('/getinformation/<string:sid>')
def getinformationa(sid):
    information = sqlite3.connect('sql/information.db')
    c = information.cursor()
    c.execute('select * from information where schid ="%s"'%sid)
    a = c.fetchall()[0]
    information.close()
    date={
            'schid':a[0],
            'nickname':a[1],
            'sex':a[2],
            'school':a[3],
            'grade':a[4],
            'sgntre':a[5],
            'sports':a[6],
            'music':a[7],
            'movie':a[8],
            'fanju':a[9],
            'whatgood':a[10],
            'zhanwang':a[11],
            'headimage':a[12]
    }
    return jsonify(date)

@app.route('/chmark',methods=['POST'])
def chmark():
    if session.get('pass') == 'homurachan' + session.get('schid') + 'homurachan':
        information = sqlite3.connect('sql/information.db')
        c = information.cursor()
        c.execute("update mark set mark1='%s',mark2='%s',mark3='%s',mark4='%s',mark5='%s',mark6='%s',mark7='%s',mark8='%s' where schid = '%s'"%(request.form.get('mark1'),request.form.get('mark2'),request.form.get('mark3'),request.form.get('mark4'),request.form.get('mark5'),request.form.get('mark6'),request.form.get('mark7'),request.form.get('mark8'),session.get('schid')))
        c.execute("update information set sports ='%s',music='%s',movie='%s',fanju='%s',whatgood='%s',zhanwang='%s' where schid='%s'"%(request.form.get('sports'),request.form.get('music'),request.form.get('movie'),request.form.get('fanju'),request.form.get('whatgood'),request.form.get('zhanwang'),session.get('schid')))
        information.commit()
        information.close()
        return jsonify({'status':'success'})

@app.route('/getmark/<string:sid>')
def getmark(sid):
    information = sqlite3.connect('sql/information.db')
    c = information.cursor()
    c.execute('select mark1,mark2,mark3,mark4,mark5,mark6,mark7,mark8,sports,music,movie,fanju,whatgood,zhanwang from mark,information where schid = "%s"'%sid)
    a = c.fetchall()[0]
    date={
            'mark1':a[0],
            'mark2':a[1],
            'mark3':a[2],
            'mark4':a[3],
            'mark5':a[4],
            'mark6':a[5],
            'mark7':a[6],
            'mark8':a[7],
            'sports':a[8],
            'music':a[9],
            'movie':a[10],
            'fanju':a[11],
            'whatgood':a[12],
            'zhanwang':a[13],
        }
    information.close()
    return jsonify(date)
    
@app.route('/findcard')
def findcard():
    if session.get('pass') == 'homurachan' + session.get('schid') + 'homurachan':
        card = sqlite3.connect('sql/card.db')
        c = card.cursor()
        c.execute('select cardID,fromID,time,whatsay from card where schid = "%s"'%session.get('schid'))
        a = c.fetchall()
        card.close()
        final ={}
        if a:
            final['status']='have'
            for b in range(len(a)):
                c={
                    'cardID':a[b][0],
                    'fromID':a[b][1],
                    'time':a[b][2],
                    'whatsay':a[b][3]
                }
                final[str(b)]=c
        else:
            final['status']='none'
        return jsonify(final)

@app.route('/getlike/<string:sid>')
def getlike(sid):
    information = sqlite3.connect('sql/information.db')
    c = information.cursor()
    c.execute("select * from mark where schid = '%s'"%sid)
    a = c.fetchall()
    information.close()
    if a:
        date={
                'schid':a[0][0],
                'mark1':a[0][1],
                'mark2':a[0][2],
                'mark3':a[0][3],
                'mark4':a[0][4],
                'mark5':a[0][5],
                'mark6':a[0][6],
                'mark7':a[0][7],
                'mark8':a[0][8]
        }
        return jsonify(date)
    else:
        return jsonify({'status':'error'})

@app.route('/killcard/<string:cid>')
def killcard(cid):
    if session.get('pass') == 'homurachan' + session.get('schid') + 'homurachan':
        card = sqlite3.connect('sql/card.db')
        c = card.cursor()
        c.execute('delete from card where cardID = "%s"'%cid)
        card.commit()
        card.close()
        return jsonify({'status':'success'})
    else:
        return jsonify({'status':'error'})

@app.route('/chng',methods=['POST'])
def chng():
    if session.get('pass') == 'homurachan' + session.get('schid') + 'homurachan':
        information = sqlite3.connect('sql/information.db')
        c = information.cursor()
        c.execute("update information set nickname = '%s', sgntre = '%s' where schid = '%s'"%(request.form.get('nickname'),request.form.get('sgntre'),session.get('schid')))
        information.commit()
        information.close()
        return jsonify({'status':'success'})

@app.route('/sendcard',methods=['POST'])
def sendcard():
    if session.get('pass') == 'homurachan' + session.get('schid') + 'homurachan':
        card = sqlite3.connect('sql/card.db')
        c = card.cursor()
        for _ in range(int(request.form.get('count'))):
            if request.form.get('tolimit')!='wu':
                c.execute("insert into card values('%s','%s',NULL,'wu','wu','%s','%s')"%(session.get('schid')+str(int(time.time())),session.get('schid'),request.form.get('whatsay'),str(time.time())))
                card.commit()
                card.close()
                return jsonify({'status':'success'})
            else:
                c.execute("insert into card values('%s','%s',NULL,'wu','%s','%s','%s')"%(session.get('schid')+str(int(time.time())),session.get('schid'),session.get('xy'),request.form.get('whatsay'),str(time.time())))
                card.commit()
                card.close()
                return jsonify({'status':'success'})

@app.route('/gethead/<string:sid>')
def gethead(sid):
    information = sqlite3.connect('sql/information.db')
    c = information.cursor()
    c.execute('select headimage from information where schid = "%s"'%sid)
    a = c.fetchall()
    information.close()
    f = open('headimage/%s.jpg'%a[0][0],'rb')
    b = f.read()
    f.close()
    return b

@app.route('/chhead',methods=['POST'])
def chhead():
    if session.get('pass') == 'homurachan' + session.get('schid') + 'homurachan':
        information = sqlite3.connect('sql/information.db')
        c = information.cursor()
        c.execute("update information set headimage='%s'"%request.form.get('imagenumber'))
        information.commit()
        information.close()
        return jsonify({'status':'success'})

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/welcome')
def indexaa():
    return render_template('welcome.html')

@app.route('/habit')
def indexaaa():
    return render_template('habit.html')

@app.route('/talk')
def indexaaaa():
    return render_template('communicate.html')

@app.route('/people')
def indexaaaaa():
    return render_template('user_information.html')

@app.route('/main')
def indexaaaaaa():
    return render_template('main.html')

@app.route('/checkfirst',methods=['GET'])
def checkfirst():
        return jsonify({'name':session.get('name'),'count':session.get('count'),'schid':session.get('schid')})

@app.route('/login',methods=['POST'])
def login():
    schid = request.form.get('username')
    token = request.form.get('token')
    information = sqlite3.connect('sql/information.db')
    c = information.cursor()
    c.execute("select nickname,school from information where schid = '%s'"%schid)
    a = c.fetchall()
    if not a:
        c.execute("select count(schid) from information")
        a = c.fetchall()
        informationa = getinformation(token)
        c.execute('insert into information (schid,nickname,sex,school,grade,headimage) values ("%s","%s","%s","%s","%s","1")'%(schid,informationa['xm'],informationa['xb'],informationa['xy'],informationa['nj']))
        c.execute('insert into mark (schid)values ("%s")'%schid)
        information.commit()
        session['name'] = informationa['xm']
        session['count'] = a[0][0]+1
        session['pass'] = 'homurachan' + schid + 'homurachan'
        session['schid'] = schid
        session['xy'] = informationa['xy']
        information.close()
        return redirect(url_for('main'))
    else:
        session['name'] = a[0][0]
        session['count'] = 0
        session['pass'] = 'homurachan' + schid + 'homurachan'
        session['schid'] = schid
        session['xy'] = a[0][1]
        information.close()
        return redirect(url_for('main'))

@app.route('/pic/<string:sid>')
def indexa(sid):
    image = open("static/pic/"+sid,'rb')
    a = image.read()
    image.close()
    return a


@app.route('/main')
def main():
    if session.get('pass') == 'homurachan' + session.get('schid') + 'homurachan':
        getcard()
        return render_template('main.html')
    else:
        return flask.abort(500)


if __name__ == '__main__':
    app.run()
