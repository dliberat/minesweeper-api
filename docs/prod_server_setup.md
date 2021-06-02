# Production Environment Setup

This guide is a work in progress.
Assumes Ubuntu 18.04 with git already installed.

### Install docker and docker compose
Follow instructions at (https://docs.docker.com/compose/install/)

### Install nginx

```
sudo apt update
sudo apt install -y nginx
```

### Clone repo

```
cd ~
git clone https://github.com/dliberat/minesweeper-api.git
```

### Create a .env file

The file `.env_debug` is provided as an example for use during development.
In production, a `.env` file is expected.

Create a `.env` file as follows, then modify it as needed.

`cp .env_debug .env`

At a bare minimum, you will probably need to add your server's IP address or DNS name to the `DJANGO_ALLOWED_HOSTS` envvar.
This envvar can take a comma-separated list of values to be added to the `ALLOWED_HOSTS` list in Django's settings.
The exact contents will depend on the nature of your reverse proxy setup.

*The security key and database parameters should also be changed and kept secret!*


### Set up UWSGI forwarding on Nginx

`cd /etc/nginx/sites-available`

Create a file called `sweeper`, with the following contents:

```
upstream django {
    server 127.0.0.1:8000;
}

server {
        listen 80 default_server;
        listen [::]80 default_server;

        server_name _;
        charset utf-8;

        client_max_body_size 50M;

        location /media {
            alias /var/www/media;
        }

        location /static {
            alias /var/www/static;
        }

        location / {
            uwsgi_pass django;
            include /home/dliberat/minesweeper-api/uwsgi_params; # wherever the repo was cloned
        }
}
```

```
sudo ln -s /etc/nginx/sites-available/sweeper /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -s reload
```

### Launch app

From the source code directory, build the container

`docker-compose -f docker-compose-prod.yml build`

Then make sure to modify permissions as needed (may need to repeat this step a few times throughout the process):

`sudo chown -R ${USER}:${USER} .`

And launch. Add the -d flag to daemonize.

`docker-compose -f docker-compose-prod.yml up`

Now test that everything is working by accessing the site via the server's public IP address on port 80.
Nginx should forward API requests to Django (e.g. (http://localhost/api/)), and serve static files by itself (e.g., (http://localhost/static/client.html))

### TO DO:

- Turn the app into a service and set to auto-start on boot
- Add HTTPS
- Set up CI/CD
