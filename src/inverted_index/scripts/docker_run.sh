#!/bin/bash

docker run -p 9000:8080  inverted-index:latest

# can now test docker image at http://localhost:9000/2015-03-31/functions/function/invocations