#!/bin/bash

host="0.0.0.0"
port=8000
config_path=""

helpFunction()
{
    echo "Usage $0 -h \"host\" -p \"port\" -c \"config_path\""
    exit 1
}

while getopts "h:p:c:" opt
do
    case "$opt" in
        h) host=$OPTARG ;;
        p) port=$OPTARG ;;
        c) config_path=$OPTARG ;;
        *) echo "Invalid option" ; helpFunction ;;
    esac
done

cmd="python -m uvicorn main:app --host $host --port $port"

if [ -z "$config_path" ]; then
    $cmd
else
    CONFIG_PATH=$config_path $cmd
fi