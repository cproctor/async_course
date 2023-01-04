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
apt install certbot nginx gh python3.10-venv pandoc pandoc-citeproc tree
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
- `ALLOWED_HOSTS=['localhost', 'lai619.chrisproctor.net']`
- `STATIC_ROOT="/opt/lai619/static_root"`
- Email:
  ```
  EMAIL_HOST = "smtp.fastmail.com"
  EMAIL_PORT = 465
  EMAIL_USE_SSL = True
  EMAIL_HOST_USER = "chris@chrisproctor.net"
  EMAIL_HOST_PASSWORD = "..."
  ```
- Configure logging (`cognitive_apprenticeship/deploy/settings_logging.py`)

Install dependencies

```
python3 -m venv /opt/lai619/env
source /opt/lai619/env/bin/activate
cd /opt/lai619/async_course
pip install -r requirements.txt
```

Setup tasks

```
./manage.py collectstatic
./manage.py migrate
deactivate
```

### Services

```
cd /opt/lai619/async_course/async_course/async_course/deploy
sudo cp gunicorn619.socket gunicorn619.service /etc/systemd/system/
sudo chown -R www-data:www-data /opt/lai619
sudo systemctl start gunicorn619
sudo systemctl status gunicorn619
```

### Networking

```
sudo cp nginx.conf /etc/nginx/nginx.conf
sudo systemctl enable nginx
sudo systemctl start nginx
sudo systemctl status nginx
```

- Set debug to False

## Future refactoring

- Add a `StudentAssignment` model with status. Currently, we handle this implicitly and it's a mess.
  - Refactor models. 
    - Submission should have a ForeignKey to StudentAssignment. 
      - Submission should have "uploader" field.
      - In assignment submission timeline, show timestamps. Also show who uploaded which versions. 
        - Email notifications and their recipients need to accurately represent who uploaded which versions. 
    - StudentAssignment should have a status field with default.
  - Refactor views.
    - Model instance lookups will get much simpler. 
    - Check whether any mixins are affected.
    - Update situations in views where student assignemnt status should be updated.
      - Ensure that when an assignemnt acceptance has been manually overridden, 
  - Refactor templates to more clearly articulate assignment status. The assignment list page should double as a gradebook.
  - Remove unnecessary management commands.
- Allow for deletion of comments and submissions.
- Apparently when I edit a review, it updates the author as well. This isn't what I intended!
- Settings.POST_UPVOTE_HOUR_LIMIT is mis-named.

## TO-DO list preparing for 2023 spring

- Publication creation should not allow slugs which can't be expressed in a URL. The site crashed with: 'jbp:/content/journals/10.1075/jnlh.7.02nar' (#1)
- In assignment thread:
  - Show a breadcrumb to past assignments (when a reviewerRole relationship exists).
- Make profile properties optional. 
- Show grades (including points)
- Make sure assignments without peer review don't show up for peers (this would be an issue with reviewer roles.)

URGENT
- Users who are not students are currently shown the roster page 
  (and students presumably could see the roster page.) When landing on an assignment, students should see the description (if they have a submission); teachers should see the roster; and non-students should see the description. 

## Curricular revision: 

- Move in a gradient from methods when we already know quite a bit about the situation, to those where we know very little. 

  - case study
  - narrative
  - ethnography
  - phenomenology
  - grounded theory

## TO-DO list initializing 2023 Spring

- Send out to all students the intro survey
- Make some pages publicly visible
  - Add a Boolean field on the Page model
  - in the logged-out view, show pages which are on menu and public
- Upload CSV of students.
