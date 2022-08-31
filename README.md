# Async Course

Note that this app is designed to be administered by a teacher who is comfortable with
the Django backend. The administrative UI is not fully-developed.

## Feature Overview

- Users are put into groups
- Users have roles

This package implements an asynchronous course. The main features 
motivating this:
- A Hacker News-style threaded, weighted discussion forum.

## Deployment

### Prepare virtual machine

Create a new VM running Ubuntu 22.04 (Digital Ocean Droplet) with SSH keys.
Ensure that domains are using DO's nameservers (`ns{1,2,3}.digitalocean.com`)
and that DO is routing domains to the droplet.
SSH in as root.

```
apt update
apt upgrade
apt install certbot nginx gh python3.10-venv tree
adduser chris
usermod -aG sudo chris
mv .ssh /home/chris/.ssh
chown -R chris:chris /home/chris/.ssh
sudo ufw allow OpenSSH
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
exit
```

Create a personal access token in [github](https://github.com/settings/tokens).
SSH in as chris and save the token in `~/github.txt`.

```
gh auth login --with-token < ~/github.txt
gh auth setup-git
export GITHUB_TOKEN="$(cat ~/github.txt)"
sudo chown -R chris:chris /opt
cd /opt
mkdir -p lai619/logs lai619/static_root
cd lai619
gh repo clone cproctor/cognitive-apprenticeship
cd /opt
gh repo clone cproctor/async_course
```

Configure app settings (`async_course/settings.py`)

- Generate secret key
  ```
  from django.core.management.utils import get_random_secret_key  
  get_random_secret_key()
  ```
- `ALLOWED_HOSTS=['localhost']`
- `STATIC_ROOT="/opt/lai619/static_root"`
- Configure logging (`cognitive_apprenticeship/deploy/settings_logging.py`)

Install dependencies

```
python3 -m venv /opt/lai619/env
source /opt/lai619/env/bin/activate
cd /opt/lai619/cognitive-apprenticeship/
pip install -r requirements.txt
```

Setup tasks

```
./manage.py collectstatic
./manage.py migrate
```

### Services

```
cd /opt/lai619/cognitive-apprenticeship/cognitive_apprenticeship/deploy
sudo cp gunicorn619.socket gunicorn619.service /etc/systemd/system/
sudo chown -R www-data:www-data /opt/lai619
sudo systemctl start gunicorn619
sudo systemctl status gunicorn619
```

### Networking

- Configure nginx (starting from `cognitive_apprenticeship/deploy/nginx.conf`)



- Set debug to False
