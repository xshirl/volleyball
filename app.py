from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy.orm import relationship 

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "volleyball.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

db = SQLAlchemy(app)

class Register(db.Model):
    __tablename__ = "register"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    team = db.Column(db.String(80), db.ForeignKey('scores.team'))
    city = db.Column(db.String(80))
    wins = db.Column(db.Integer, db.ForeignKey('scores.wins'), default=0, )
    losses = db.Column(db.Integer, db.ForeignKey('scores.losses'),  default=0,)
    points = db.Column(db.Integer, db.ForeignKey('scores.points'),  default=0, )
    rank = db.Column(db.Integer, db.ForeignKey('scores.rank'), default=0)
    score = relationship("Scores", foreign_keys=[team, wins, losses, points, rank], back_populates="register")
    def __repr__(self):
        return f"Register('{self.team}', '{self.city}')"

class Scores(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    court = db.Column(db.String(80))
    game = db.Column(db.String(80))
    team = db.Column(db.String(80))
    score = db.Column(db.String(80))
    wins = db.Column(db.Integer, default= 0)
    losses = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)
    rank = db.Column(db.Integer, default=0)
    # register = relationship("Register", foreign_keys=[team, wins, losses, points, rank], back_populates="score")
@app.route("/")
def home():
    return render_template('index.html')

@app.route("/register", methods=['POST', 'GET'])
def register():
    team = Register(team=request.form.get("team"), city=request.form.get("city"))
    db.session.add(team)
    db.session.commit()
    registers = Register.query.all()
    print(registers)
    return render_template("register.html", registers=registers)

@app.route("/scores", methods=['POST', 'GET'])
def scores():
    court = Scores(court=request.form.get("court"), game=request.form.get("game"), team=request.form.get("team"), score=request.form.get("score"))
    db.session.add(court)
    db.session.commit()
    scores = Scores.query.all()
    for i in range(len(scores)):
        for j in range(len(scores)):
            if scores[i].court == scores[j].court and scores[i].game == scores[j].game:
                if scores[i].score > scores[j].score:
                    scores[i].wins += 1
                    scores[j].losses += 1
                    scores[i].points += (scores[i].score - scores[j].score)
                    scores[j].points += (scores[j].score - scores[i].score)
                    scores[i].rank +=1
                elif scores[i].score < scores[j].score:
                    scores[j].wins += 1
                    scores[j].rank += 1 
                    scores[i].losses += 1
                    scores[i].points += (scores[i].score - scores[j].score)
                    scores[j].points += (scores[j].score - scores[i].score)
                elif scores[i].score == scores[j].score:
                    if scores[i].wins > scores[i].wins:
                        scores[i].rank += 1
                    elif scores[j].wins > scores[i].wins:
                        scores[j].rank +=1
                    elif scores[i].wins == scores[j].wins:
                        if scores[i].points > scores[j].points:
                            scores[i].rank +=1
                        elif scores[j].points > scores[i].points:
                            scores[j].rank +=1


    return render_template("scores.html", scores=scores)

if __name__ == '__main__':
   app.run(debug=True)