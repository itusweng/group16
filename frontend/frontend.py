from flask import Flask, redirect, url_for, render_template, request, session
import requests
from PIL import Image
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'blg411e'

@app.route("/login", methods = ['GET','POST'])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form['name']
        password = request.form['password']
        print(username)
        print(password)

        headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded',}
        data = {'username': '{}'.format(username), 'password': '{}'.format(password)}
        response = requests.post('http://127.0.0.1:8000/login', headers=headers, data=data)

        print(response.status_code)

        if int(response.status_code) == 200:
            print("success")
            print(response.text)
            res = response.json()
            token = res['access_token']
            session["islogin"] = True
            session["token"] = token
            return redirect("/mainqr")
        elif int(response.status_code) != 200:
            print("fail")
            return render_template("login.html", message = "Wrong login credentials!")
        else:
            return render_template("login.html", message = "An Error has occured please try again")

@app.route("/signup", methods = ['GET','POST'])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    elif request.method == "POST":
        username = request.form['name']
        email = request.form['email']
        password = request.form['password']
        password2 = request.form['password2']

        if password != password2:
            return render_template("signup.html", message="Passwords does not match!",msg = "")

        if '@' not in email:
            return render_template("signup.html", message="Wrong e-mail input!",msg = "")

        if len(username) == 0 or len(email) == 0 or len(password) == 0:
            return render_template("signup.html", message="Please fill all the input fields",msg = "")

        headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded',}
        data = {'username': '{}'.format(username), 'email': '{}'.format(email), 'password': '{}'.format(password)}
        response = requests.post('http://127.0.0.1:8000/register', headers=headers, data=data)

        if int(response.status_code) == 200:
            print("success")
            print(response.text)
            return render_template("signup.html", message = "", msg = "Register Completed Click Login to Authenticate")
        elif int(response.status_code) != 400:
            print("fail")
            return render_template("signup.html", message = "User already exists please try another username!",msg = "")
        else:
            return render_template("signup.html", message = "An Error has occured please try again!",msg = "")


@app.route("/home", methods = ['GET','POST'])
def home():
    session['qid'] = None
    session['url'] = None
    session['has_id'] = False
    session["islogin"] = False
    session["token"] = None
    if request.method == "GET":
        return render_template("home.html")

@app.route("/mainqr", methods = ['GET','POST'])
def myqr():
    session['qid'] = None
    session['url'] = None
    session['has_id'] = False
    if request.method == "GET":
        if session["islogin"]:
            mainArray = []
            headers = {'accept': 'application/json', 'Authorization': 'Bearer {}'.format(session['token'])}
            get_response = requests.get('http://127.0.0.1:8000/my_qr_codes', headers=headers)
            if (get_response.status_code == 200):
                res = get_response.json()
                print(res)
                for i in res:
                    mainArray.append([i['qr_id'],i['link']])
            print(mainArray)
            return render_template("mainqr.html", rows = mainArray)
        else:
            return redirect("/home")
    elif request.method == "POST":
        print(request.form)
        if session["islogin"]:
            if list(request.form.keys())[0] == "update":
                qid, url = str(request.form['update']).split("|")
                session['qid'] = qid
                session['url'] = url
                session['has_id'] = True
                return redirect("/updateqr")
            elif list(request.form.keys())[0] == "stats":
                session['qid'] = request.form['stats']
                session['has_id'] = True
                return redirect("/stats")
            elif list(request.form.keys())[0] == "createnew":
                headers = {'accept': 'application/json', 'Authorization': 'Bearer {}'.format(session['token']),'Content-Type': 'application/x-www-form-urlencoded',}
                data = {'link': '{}'.format(request.form['createnew'])}
                response = requests.post('http://127.0.0.1:8000/create_qr', headers=headers, data=data)
                return redirect("/mainqr")
            elif list(request.form.keys())[0] == "create":
                qid, url = str(request.form['create']).split("|")
                session['qid'] = qid
                session['url'] = url
                session['has_id'] = True
                return redirect("/qrcodegenerator")
            elif list(request.form.keys())[0] == "delete":
                delete_id = request.form['delete']
                headers = {'accept': 'application/json', 'Authorization': 'Bearer {}'.format(session['token'])}
                delete_response = requests.post('http://127.0.0.1:8000/delete_qr?qr_id={}'.format(delete_id),headers=headers)
                return redirect("/mainqr")
            elif list(request.form.keys())[0] == "premium":
                headers = {'accept': 'application/json', 'Authorization': 'Bearer {}'.format(session['token'])}
                response = requests.get('http://127.0.0.1:8000/set_premium', headers=headers)
                return redirect("/mainqr")


@app.route("/qrcodegenerator", methods = ['GET','POST'])
def create():
    if request.method == "GET":
        if session["islogin"]:
            return render_template("qrcodegenerator.html")
        else:
            return redirect("/home")
    elif request.method == "POST":
        f = request.files['file']
        if f:
            f = request.files['file']
            f.save(f.filename)
            version = request.form['version']
            size = request.form['size']
            headers = {'accept': 'application/json', 'Authorization': 'Bearer {}'.format(session['token'])}
            params = (('qr_id', '{}'.format(session['qid'])),('version', '{}'.format(version)),('size', '{}'.format(size)),)
            files = {'file': ('{}'.format(f.filename), open('{}'.format(f.filename), 'rb'))}

            response = requests.post('http://127.0.0.1:8000/get_qr_img', headers=headers, params=params, files=files)
            img = Image.open(io.BytesIO(response.content))
            img.save("static/temp.jpg")

            print(response.content)
            print(response.status_code)
            return render_template("qrcodegenerator.html", check = True)
        else:
            version = request.form['version']
            size = request.form['size']
            headers = {'accept': 'application/json', 'Authorization': 'Bearer {}'.format(session['token'])}
            params = (('qr_id', '{}'.format(session['qid'])),('version', '{}'.format(version)),('size', '{}'.format(size)),)
            response = requests.post('http://127.0.0.1:8000/get_qr_img', headers=headers, params=params)
            img = Image.open(io.BytesIO(response.content))
            img.save("static/temp.jpg")
            print(response.content)
            print(response.status_code)
            return render_template("qrcodegenerator.html", check = True)



@app.route("/logout", methods = ['GET','POST'])
def logout():
    if request.method == "GET":
        session["islogin"] = False
        session["token"] = None
        session['qid'] = None
        session['url'] = None
        session['has_id'] = False
        return redirect("/home")

@app.route("/updateqr", methods = ['GET','POST'])
def updateqr():
    if request.method == "GET":
        if session["islogin"]:
            return render_template("updateqr.html")
        else:
            return redirect("/home")
    elif request.method == "POST":
        headers = {'accept': 'application/json', 'Authorization': 'Bearer {}'.format(session['token'])}
        params = (('qr_id', '{}'.format(session['qid'])),('new_link', '{}'.format(request.form['newurl'])))
        response = requests.post('http://127.0.0.1:8000/update_qr', headers=headers, params=params)

        return redirect("/mainqr")

@app.route("/stats", methods = ['GET','POST'])
def statsqr():
    if request.method == "GET":
        if session["islogin"]:
            mainArray = []
            headers = {'accept': 'application/json', 'Authorization': 'Bearer {}'.format(session['token'])}
            get_response = requests.get('http://127.0.0.1:8000/get_qr_stats?qr_id={}'.format(session['qid']), headers=headers)
            if (get_response.status_code == 200):
                res = get_response.json()
                print(res)
                for i in res:
                    tm = str(i['time'])
                    tm = tm.replace("T"," ")
                    mainArray.append([tm,i['country'],i['latitude'],i['longitude']])
            print(mainArray)
            session['qid'] = None
            session['has_id'] = False
            return render_template("stats.html",rows = mainArray)
        else:
            return redirect("/home")
    elif request.method == "POST":
        return redirect("/mainqr")
"""
@app.route("/profile", methods = ['GET','POST'])
def profile():
    if request.method == "GET":
        if session["islogin"]:
            return render_template("profile.html")
        else:
            return redirect("/home")
    elif request.method == "POST":
        headers = {'accept': 'application/json', 'Authorization': 'Bearer {}'.format(session['token'])}
        response = requests.get('http://127.0.0.1:8000/set_premium', headers=headers)
        return redirect("/profile")
"""
if __name__ == "__main__":
    app.run(debug=True)