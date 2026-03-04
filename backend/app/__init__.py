from flask import Flask 
from .config import Config
from flask_cors import CORS

from os import name    
from .functions import DB 
from .mqtt import MQTT  

# Create MongoDB instance to get access to all the functions defined in functions.py
mongo = DB(Config)
Mqtt  = MQTT(mongo)

app = Flask(__name__)
app.config.from_object(Config) 
CORS(app)

from app import views