from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars
import pandas as pd
from bs4 import BeautifulSoup
# Create an instance of Flask
app = Flask(__name__)

# Use PyMongo to establish Mongo connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_db")

@app.route("/")
def home():
    # Find one record of data from the mongo database
    mars_data = mongo.db.mars_collection.find_one()
    print(mars_data)
    # Return template and data
    return render_template("index.html", planet=mars_data,hemisphere=mars_data['hemisphere_image_urls'],featured_imgs=mars_data['featured_img_url'])

@app.route("/scrape")   
def scrape():
    # Run the scrape function
    mars_data = scrape_mars.scrape_info()
    # Update the Mongo database using update and upsert=True
    #mongo.db.mars_collection.drop()
    #mongo.db.mars_collection.insert_one(mars_data)
    mongo.db.mars_collection.update_one({}, mars_data, upsert=True)
    # #insert a python dictionary returned by function scrape() as a collection
    # mongo.db.mars_collection.insert_one(mars_data)

    # Redirect back to home page
    return redirect("/", 302)



if __name__ == "__main__":
    app.run(debug=True)