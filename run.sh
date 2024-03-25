#!/bin/bash

source ~/.bashrc
source setup.bash
# flask run
waitress-serve --listen=0.0.0.0:65500 server:app
