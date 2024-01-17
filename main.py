from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from datetime import datetime
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from string import ascii_uppercase
import forms
import aiapi
import config

rooms = {}
app = Flask(__name__)
app.config.from_object(config.config['development'])
socketio = SocketIO(app)

#-------------------- setup SQL DB -----------------------#
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stories.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

Bootstrap(app)

# Configure Table
class AddStory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(80))
    title = db.Column(db.String(250))
    story = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        
        if code not in rooms:
            break
    
    return code




@app.route("/", methods=["POST", "GET"])
def home():
    session.clear()
    return render_template("home.html")


@app.route("/create", methods =["POST", "GET"])
def create():
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            flash("Please insert a name")
            return redirect(next or url_for("create"))
        else:
            code = generate_unique_code(4)
            room = code
            rooms[room] = {"members": 0, "messages": []}
            session["room"] = room
            session["username"] = username
            return redirect(url_for("room"))
    return render_template("create.html")

    
@app.route("/room", methods=["POST", "GET"])
def room():
    room = session.get("room")
    if room is None or session.get("username") is None or room not in rooms:
        return redirect(url_for("home"))
    return render_template("room.html", code=room, messages=rooms[room]["messages"])

@app.route("/join", methods=["POST", "GET"])
def join():
    if request.method == "POST":
        username = request.form.get("username")
        code = request.form.get("code")
        
        if not username:
            flash("PLease insert a name")
            return redirect(next or url_for("join"))
        if not code:
            flash("Plsease eneter a room code")
            return redirect(next or url_for("join"))
        room = code
        if code not in rooms:
            flash("Room does not exist.")
        else:
            session["room"] = room
            session["username"] = username
            return redirect(url_for("room"))
    return render_template("join.html")

#Join the initialized room, if there is
@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    username = session.get("username")
    print(rooms)
    if not room or not username:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"username": username, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"{username} joined room {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    username = session.get("username")
    leave_room(room)
    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    send({"username": username, "message": "has left the room"}, to=room)
    print(f"{username} left room {room}")

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return
    content = {
        "username": session.get("username"),
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('username')} said: {data['data']}", to=room)

@app.route("/sharestory", methods=["POST", "GET"])
def sharestory():
    form = forms.AddStoryForm(request.form)
    if request.method == "POST":
        author = form.author.data
        title = form.title.data
        story = form.story.data
        addstory = AddStory(author=author,title=title, story=story)
        
        db.session.add(addstory)
        db.session.commit()
        flash(f"Thank you for sharing!")
        return redirect(url_for("get_all_stories"))
    return render_template("sharestory.html")

@app.route('/allstories', methods=["GET"])
def get_all_stories():
    stories = AddStory.query.all()
    return render_template("stories.html", all_stories=stories)

@app.route("/story/<int:story_id>")
def show_story(story_id):
    requested_story = AddStory.query.get(story_id)
    return render_template("story.html", story=requested_story)

@app.route("/chatty", methods= ['POST', 'GET'])
def chatty():
   if request.method == 'POST':
       prompt = request.form['prompt']
       res = {}
       res['answer'] = aiapi.generate_chat_response(prompt)
       print(prompt)
       print(res)
       return jsonify(res), 200

   return render_template("chatty.html")

if __name__ == "__main__":
    socketio.run(app, debug=True)


