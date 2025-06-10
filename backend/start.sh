#!/bin/bash
flask run --host=0.0.0.0 --port=10000
gunicorn app:app --timeout 120
