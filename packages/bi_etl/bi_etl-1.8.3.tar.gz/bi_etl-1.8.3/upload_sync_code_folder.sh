[[ -z "$1" ]] && { echo "Parameter 1 is empty" ; exit 1; }

rsync -rt --progress $2 --exclude *__pycache__ --exclude=test_config.ini --exclude="*.pyo" --exclude "*.pyc" --exclude .idea --exclude .tox --exclude .venv --exclude *.kbdx --exclude .idea --exclude config.ini --delete ~/code/$1/ derekiw@bietl.dev:upload/$1

