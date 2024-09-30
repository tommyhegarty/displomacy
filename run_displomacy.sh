#!/bin/bash

# file to run the displomacy bot + game runner code

TOKEN=$(aws ssm get-parameter --name "/displomacy/token" | jq --raw-output '.Parameter.Value')
export TOKEN

echo "starting the displomacy python file"
nohup python src/displomacy.py > execution.log 2>&1 &