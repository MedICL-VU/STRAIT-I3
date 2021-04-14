
import torch
from flask_ngrok import run_with_ngrok
import requests
from flask import Flask, request, jsonify
app = Flask(__name__)
run_with_ngrok(app)  # starts ngrok when the app is run
@app.route("/")
def home():
    gpu_name = torch.cuda.get_device_name(0)
    return "<h1>Connected to Google Colab!</h1><p>GPU affected: {}</p>".format(gpu_name)

@app.route("/run",methods=['GET','POST'])
def run():
    name = request.json['model']
    docker = request.json['docker']
    config = request.json['config']
    print(name)

    return jsonify({"":torch.cuda.get_device_name(0)})

app.run()