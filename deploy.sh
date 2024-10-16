#!/bin/bash
 
# Activate the virtual environment
source /home/ekraumj/genai_demo/.myEnv/bin/activate
 
# Deploy
 
nohup python -u api.py > app.log 2>&1 &
