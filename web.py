from flask import Flask, render_template, request
import sqlite3
import json

app = Flask(__name__)

@app.route("/data.json")
def data():
    connection = sqlite3.connect("hakku.db")
    cursor = connection.cursor()
    cursor.execute("SELECT timestamp, temp from temps")
    results = cursor.fetchall()
    print(results)
    return json.dumps(results)

@app.route("/graph")
def graph():
    return render_template('graph.html')

if __name__ == '__main__':
    app.run(
    debug=True,
    threaded=True,
    host='0.0.0.0'
)
