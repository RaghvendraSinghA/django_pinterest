#!/usr/bin/env bash
set -o errexit

# set -o errexit is a shell option that makes a script stop immediately if any command fails. It’s identical to set -e.

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate