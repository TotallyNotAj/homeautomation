"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file creates your application.
"""

# from crypt import methods
import site 

from app import app, Config,  mongo, Mqtt
from flask import escape, render_template, request, jsonify, send_file, redirect, make_response, send_from_directory 
from json import dumps, loads 
from werkzeug.utils import secure_filename
from datetime import datetime,timedelta, timezone
from os import getcwd
from os.path import join, exists
from time import time, ctime
from math import floor
 



#####################################
#   Routing for your application    #
#####################################


# 1. CREATE ROUTE FOR '/api/set/combination'
@app.route('/api/set/combination', methods=['POST'])
def set_combination():
    if request.method == "POST":
        try:
            passcode = request.form.get("passcode")

            #Must be integer and exactly 4 digits
            if passcode is None or len(passcode) != 4 or not passcode.isdigit():
                return jsonify({"status": "failed", "data": "failed"})

            result = mongo.setPasscode(passcode)

            if result:
                return jsonify({"status": "complete", "data": "complete"})

        except Exception as e:
            print(f"set_combination error: {str(e)}")

    return jsonify({"status": "failed", "data": "failed"})

# 2. CREATE ROUTE FOR '/api/check/combination'
@app.route('/api/check/combination', methods=['POST'])
def check_combination():
# Retrieve the passcode from the 'code' collection in the database
    if request.method == "POST":
        passcode = request.form.get('passcode')
        try:
        # Validate passcode against the 'code' collection
            count = mongo.checkPasscode(passcode)
            if count > 0:
                return jsonify({"status": "complete", "data": "complete"})
            else:
                return jsonify({"status": "failed", "data": "failed"})
        except Exception as e:
                msg = str(e)
                print(f"check_combination Error: {msg}")
                return jsonify({"status": "failed", "data": "failed"})

# 3. CREATE ROUTE FOR '/api/update'
@app.route('/api/update', methods=['POST'])
def update_data():
    '''Updates the 'radar' collection'''
    if request.method == "POST":
        try:
            jsonDoc= request.get_json()
            # Update the document in the 'code' collection with the new passcode

            timestamp = datetime.now().timestamp()
            timestamp = floor(timestamp)
            jsonDoc['timestamp'] = timestamp

            Mqtt.publish("620172829", dumps(jsonDoc))
            Mqtt.publish("620172829_pub",dumps(jsonDoc))
            Mqtt.publish("620172829_sub",dumps(jsonDoc))

            print(f"MQTT: {jsonDoc}")

            item = mongo.mongo.update(jsonDoc)
            if item:
                return jsonify({"status": "complete", "data": "complete"})
        except Exception as e:
            msg = str(e)
            print(f"update Error: {msg}")
        return jsonify({"status": "failed", "data": "failed"})

# 4. CREATE ROUTE FOR '/api/reserve/<start>/<end>'
@app.route('/api/reserve/<start>/<end>', methods=['GET']) 
def getAllRange(start,end):   
    start = int(start)
    end = int(end)
    '''RETURNS ALL THE DATA FROM THE DATABASE THAT EXIST IN BETWEEN THE START AND END TIMESTAMPS'''
 
    if request.method == "GET":
        '''Add your code here to complete this route'''
        try:
            item = mongo.getAllRange(start,end)
            data= list(item)
            if data:
                return jsonify({"status":"complete","data": data})
            
        except Exception as e:
            print(f"getAllRange error: f{str(e)}") 
        return jsonify({"status":"not found","data":[]})

# 5. CREATE ROUTE FOR '/api/avg/<start>/<end>'
@app.route('/api/avg/<start>/<end>', methods=["GET"])
def avg(start, end):
    if request.method == "GET":
        try:
            START = escape(start)
            END = escape(end)
            data = mongo.avgReserve(START, END)

            if data:
                return jsonify({"status":"complete", "data":data})
            
        except Exception as e:
            print(f"set_combination error: f{str(e)}")

    return jsonify({"status":"failed", "data":0})


@app.route('/api/file/get/<filename>', methods=['GET']) 
def get_images(filename):   
    '''Returns requested file from uploads folder'''
   
    if request.method == "GET":
        directory   = join( getcwd(), Config.UPLOADS_FOLDER) 
        filePath    = join( getcwd(), Config.UPLOADS_FOLDER, filename) 

        # RETURN FILE IF IT EXISTS IN FOLDER
        if exists(filePath):        
            return send_from_directory(directory, filename)
        
        # FILE DOES NOT EXIST
        return jsonify({"status":"file not found"}), 404


@app.route('/api/file/upload',methods=["POST"])  
def upload():
    '''Saves a file to the uploads folder'''
    
    if request.method == "POST": 
        file     = request.files['file']
        filename = secure_filename(file.filename)
        file.save(join(getcwd(),Config.UPLOADS_FOLDER , filename))
        return jsonify({"status":"File upload successful", "filename":f"{filename}" })

 


###############################################################
# The functions below should be applicable to all Flask apps. #
###############################################################


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page. If we wanted
    to we could change max-age to 600 seconds which would be 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.errorhandler(405)
def page_not_found(error):
    """Custom 404 page."""    
    return jsonify({"status": 404}), 404



