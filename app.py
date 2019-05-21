from flask import Flask, render_template, redirect, jsonify
from flask_pymongo import PyMongo
from sodapy import Socrata
import time
import json
from bson import json_util

app = Flask(__name__)


# establish a connection to mongodb and create table ny_potholes
mongo = PyMongo(app, uri="mongodb://localhost:27017/ny_potholes")

# route to the main html page
@app.route("/")
def home():
	return render_template("index.html")

# connect to the city of NY API and extract the first 2000 observations and insert into db
@app.route("/api/v1.0/getdata")
def getData():
	print("Fetching data")
	#drop mongo data from db if exists 
	mongo.db.data.drop()
	#call the socrata client to get first 2000 potholes 
	client = Socrata("data.cityofnewyork.us", None)
	results = client.get("fed5-ydvq", limit=2000)
	#insert data to mongodb 
	new_result = results
	time.sleep(25)
	mongo.db.data.insert_many(new_result)

	return (
		f"Inserted into the database and there are <strong>{mongo.db.data.count()}</strong> documents.<br><br>"
		f"Now let's render the data! Click the below link to render data:"
        f"<ul><li><a href='http://127.0.0.1:5000/api/v1.0/renderdata'>/api/v1.0/renderdata</a><br/></li></ul>"
	)


# routes for other html pages
@app.route("/aboutus")
def about():
	return render_template("aboutus.html")

@app.route("/visualization")
def visualize():
	return render_template("visualization.html")

# route to render data from db into table
@app.route("/data")
def data():
	
	db_data  = list(mongo.db.data.find())
	
	# json.dumps(docs_list, default=json_util.default)
	return render_template("data.html", potholeData= db_data[:200])

@app.route("/refreshdata")
def refreshgetData():
	print("fetching data")
	#drop mongo data from db if exists 
	mongo.db.data.drop()
	#call the socrata client to get first 2000 potholes 
	client = Socrata("data.cityofnewyork.us", None)
	results = client.get("fed5-ydvq", limit=2000)
	#insert data into mongodb 
	new_result = results
	time.sleep(25)
	mongo.db.data.insert_many(new_result)
	print("reloading page")
	# rediret to data.html and update table
	return redirect("/data")

	



	
if __name__ == '__main__':
	app.run(debug=True)