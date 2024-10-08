#!/bin/bash

# file to run the displomacy bot + game runner code

TOKEN=$(aws ssm get-parameter --name "/displomacy/token" | jq --raw-output '.Parameter.Value')
export TOKEN

SRC_DIR="/home/ec2-user/displomacy/src"
BOT_PATH="${SRC_DIR}/displomacy.py"
RESP_PATH="${SRC_DIR}/responder.py"

PID_DIR="/var/run"
BOT_PID="${PID_DIR}/displomacy.pid"
RESP_PID="${PID_DIR}/responder.pid"

echo "installing the requirements file"
pip install -r src/requirements.txt

start_bot() {

    if [[ -f "${BOT_PID}" ]]; then
        echo "The bot is already running..."
    else
        nohup python "${BOT_PATH}" &> /dev/null &
        echo $! > "${BOT_PID}"
        echo "Displomacy Bot has started."
    fi

}

stop_bot() {

    if [[ -f "${BOT_PID}" ]]; then
        kill "$(cat "${BOT_PID}")"
        rm "${BOT_PID}"
        echo "Displomacy bot has stopped."
    else
        echo "The bot is not running..."
    fi

}

start_resp() {

    if [[ -f "${RESP_PID}" ]]; then
        echo "The responder is already running..."
    else
        nohup python "${RESP_PATH}" &> /dev/null &
        echo $! > "${RESP_PID}"
        echo "Displomacy responder has started."
    fi

}

stop_resp() {

    if [[ -f "${RESP_PID}" ]]; then
        kill "$(cat "${RESP_PID}")"
        rm "${RESP_PID}"
        echo "Displomacy responder has stopped."
    else
        echo "The responder is not running..."
    fi

}

restart_all() {

    stop_bot
    stop_resp
    start_resp
    start_bot

}

case "$1" in
    bot-start)
        start_bot
        ;;
    bot-stop)
        stop_bot
        ;;
    resp-start)
        start_resp
        ;;
    resp-stop)
        stop_resp
        ;;
    restart)
        restart_all
        ;;
    *)
        echo "Usage: $0 {bot-start|bot-stop|resp-start|resp-stop|restart}"
esac