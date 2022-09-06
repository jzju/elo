from flask import Flask, current_app, jsonify, request
import pymongo

client = pymongo.MongoClient()
db = client.elo.players
app = Flask(__name__)


@app.route("/")
def index():
    return current_app.send_static_file("index.html")


@app.route("/players")
def players():
    ret = sorted([[p["name"], int(p["elo"])] for p in db.find()], key=lambda x: -x[1])
    print(ret)
    return jsonify(ret)


@app.route("/add")
def add():
    if request.args["name"] and not db.find_one({"name": request.args["name"]}):
        db.insert_one({"name": request.args["name"], "elo": 1000})
    return ""


@app.route("/res")
def res():
    gameOver(request.args["win"], request.args["lose"])
    return ""


def gameOver(winner, loser):
    if winner == loser:
        return
    welo = db.find_one({"name": winner})["elo"]
    lelo = db.find_one({"name": loser})["elo"]
    result = 1 / ((10.0 ** ((lelo - welo) / 400.0)) + 1)
    db.update_one({"name": winner}, {"$set": {"elo": welo + 50 * (1 - result)}})
    db.update_one({"name": loser}, {"$set": {"elo": lelo + 50 * (result - 1)}})


if __name__ == "__main__":
    app.run()
