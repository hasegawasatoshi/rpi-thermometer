#!/bin/bash

autopep8 -ivr --max-line-length 120 .
isort .
