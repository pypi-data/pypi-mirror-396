[[ -z "$1" ]] && { echo "Parameter 1 is empty" ; exit 1; }

rsync -rt --progress $2 --exclude *__pycache__ --exclude="*.pyo" --exclude=test_config.ini --exclude="*.pyc" --exclude .idea --exclude .tox --exclude .venv --excluder="*.kbdx" --exclude .idea --exclude config.ini --delete derekiw@bietl.dev:upload/$1/ ~/code/$1
