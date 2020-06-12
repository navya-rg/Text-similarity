from flask import Flask, request, redirect, render_template, url_for
import dill
dill.load_session('textsimilarity_env.db')
import mysql.connector

app = Flask(__name__)

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="17bce2416",
  database="queryvit",
  auth_plugin="mysql_native_password"
)

user=""
userid=0

@app.route('/')
def index():
    global user
    global userid
    return render_template("index.html", user=user, id="index")

@app.route('/login/<destination>', methods=['GET', 'POST'])
def login(destination):
    global user
    global userid
    if(request.method=='GET'):
        return render_template("login.html", user=user, destination=destination, id="login")
    else:
        email=request.form['email']
        password=request.form['password']
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM users where email='"+email+"';");
        myresult = mycursor.fetchone()
        if not myresult or myresult[4]!=password:
            return "Incorrect email id or password."
        user = myresult[1]
        userid = myresult[0]
        while(destination.find('+', 0)!=-1):
            destination = destination.replace('+', '/')
        print(destination)
        if destination=='/logout':
            destination=""
        return redirect("http://127.0.0.1:5000"+destination)

@app.route('/logout')
def logout():
    global user
    global userid
    user=""
    userid=0
    return render_template("index.html", user=user, id="index")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    global user
    global userid
    if (request.method == 'GET'):
        return render_template("signup.html", user=user, id="login")
    else:
        name = request.form['name']
        regno = request.form['regno']
        email = request.form['email']
        password = request.form['password']
        branch = request.form['branch']
        mycursor = mydb.cursor()
        mycursor.execute("SELECT COUNT(*) FROM users where email='" + email + "';");
        myresult = mycursor.fetchone()
        if(myresult[0]>0):
            return "User already exists"
        sql = "INSERT INTO users (name, email, regno, password, branch) VALUES (%s, %s, %s, %s, %s);"
        val = (name, email, regno, password, branch)
        mycursor.execute(sql, val)
        mydb.commit()
        mycursor.execute("SELECT * FROM users where email='" + email + "';");
        myresult = mycursor.fetchone()
        user = name
        userid = myresult[0]
        return render_template("index.html", user=user)

@app.route('/category/<cat>')
def category(cat):
    mycursor = mydb.cursor()
    mycursor.execute("select questions.qid,questions.question, count(answers.qid) from questions, answers where questions.qid=answers.qid and questions.category='"+cat+"' group by qid order by count(answers.qid) desc;");
    myresult = mycursor.fetchall()

    '''ans=[]
    for x in myresult:
        mycursor.execute("select * from answers where qid='"+str(x[0])+"';");
        myresult2 = mycursor.fetchall()
        ans.extend(myresult2)'''

    mycursor.execute("select questions.qid, questions.question, 0 from questions left join answers on questions.qid=answers.qid where answers.qid is null and category='"+cat+"';");
    myresult.extend(mycursor.fetchall())
    if cat=='roomcounselling':
        cat='room counselling'
    print(myresult)
    return render_template('category.html', user=user, myresult=myresult, cat=cat.capitalize(), id="category")

@app.route('/search', methods=['POST'])
def search():
    category = request.form['category'].replace(" ", "").lower()
    question = request.form['question']
    myresult = getSimilar(question, category)
    mycursor = mydb.cursor()
    ans = []
    for i in range (len(myresult)):
        mycursor.execute("select * from answers where qid='" + str(myresult[i][0]) + "';");
        myresult2 = mycursor.fetchall()
        temp = []
        for t in myresult[i]:
            temp.append(t)
        temp.append(len(myresult2))
        temp = tuple(temp)
        myresult[i] = temp
        ans.extend(myresult2)
    return render_template('category.html', user=user, myresult=myresult, ans=ans, cat=question, id="category")

@app.route('/postQuestion', methods=['GET', 'POST'])
def postQuestion():
    global user
    global userid
    if request.method=='POST':
        cat=request.form['category']
        question=request.form['question']
        sim=getSimilar(question, cat)
        if not sim:
            addQuestion(question, cat)
            return redirect("http://127.0.0.1:5000/category/"+cat)
        else:
            sim.sort(key=lambda x: x[3])
            sim = sim[::-1]
            score = sim[0][3]
            return render_template('similarQuestions.html', user=user, myresult=sim, id="", similarity=score, question=question, cat=cat)
    elif user and request.method=='GET':
        return render_template("postQuestion.html", user=user, id="postQuestion")
    elif request.method=='GET':
        return redirect("http://127.0.0.1:5000/login/+postQuestion")

@app.route('/continueToPost', methods=['POST'])
def continueToPost():
    global user
    global userid
    cat = request.form['category']
    question = request.form['question']
    addQuestion(question, cat)
    return redirect("http://127.0.0.1:5000/category/" + cat)

@app.route('/answerQuestion', methods=['GET', 'POST'])
def answerQuestion():
    global user
    global userid
    if request.method=='POST':
        id = request.form['id']
        answer = request.form['answer']
        addAnswer(id, answer)
        print(id+" "+answer)
        return redirect(url_for('viewAnswer', id=id))
    elif user and request.method=='GET':
        mycursor = mydb.cursor()
        mycursor.execute("select questions.qid, questions.question, 0 from questions left join answers on questions.qid=answers.qid where answers.qid is null;");
        myresult = mycursor.fetchall()
        if(len(myresult)<10):
            mycursor.execute("select questions.qid,questions.question, count(answers.qid) from questions, answers where questions.qid=answers.qid group by qid order by count(answers.qid);");
            myresult.extend(mycursor.fetchall())
        #print(myresult)
        return render_template('answerQuestion.html', user=user, myresult=myresult, id="answerQuestion")
    else:
        return redirect("http://127.0.0.1:5000/login/+answerQuestion")
        #return render_template("login.html", user=user)

@app.route('/viewAnswer/<id>')
def viewAnswer(id):
    mycursor = mydb.cursor()
    mycursor.execute("select question from questions where qid='" + id + "';")
    myresult = mycursor.fetchone()[0]
    mycursor.execute("select * from answers where qid='" + id + "';")
    ans = mycursor.fetchall()
    return render_template('viewAnswer.html', user=user, myresult=myresult, ans=ans, id="category")

def getSimilar(question, category):
    mycursor = mydb.cursor()
    mycursor.execute("SELECT qid, question FROM questions where category='"+category+"'")
    myresult = mycursor.fetchall()
    sim = []
    for x in myresult:
        score=0
        try:
            score = similarity(x[1], question) * 100
        except:
            score = 0
        print(score)
        if((score==0 and x[1].lower()==question.lower()) or score > 60):
            mycursor.execute("SELECT count(*) FROM answers where qid='" + str(x[0]) + "'")
            answers = mycursor.fetchall()
            temp=[]
            for t in x:
                temp.append(t)
            temp.append(answers[0][0])
            temp.append(score)
            temp = tuple(temp)
            sim.append(temp)
    print(sim)
    return sim

def addQuestion(question, category):
    category = category.lower()
    category = category.replace(" ", "")
    mycursor = mydb.cursor()
    sql = "INSERT INTO questions (question, uid, category) VALUES (%s, %s, %s);"
    print(userid)
    print(user)
    val = (question, userid, category)
    mycursor.execute(sql, val)
    mydb.commit()

def addAnswer(id, answer):
    mycursor = mydb.cursor()
    sql = "INSERT INTO answers (answer, uid, qid) VALUES (%s, %s, %s);"
    val = (answer, userid, id)
    mycursor.execute(sql, val)
    mydb.commit()


if __name__ == "__main__":
    app.run(debug=True)

