# Production Environment Setup

This guide is a work in progress.
Assumes Ubuntu 18.04 with git already installed.

### Install docker and docker compose

Follow instructions at (https://docs.docker.com/compose/install/).
Don't forget to add your user account to the `docker` group so that you can run Docker without sudo.

```bash
sudo usermod -aG docker $USER
```


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
        listen [::]:80 default_server;

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

If you run into permissions issues, you may need to run the following command to reset permissions in the folder.

`sudo chown -R ${USER}:${USER} .`

And launch. Add the -d flag to daemonize.

`docker-compose -f docker-compose-prod.yml up`

Now test that everything is working by accessing the site via the server's public IP address on port 80.
Nginx should forward API requests to Django (e.g. (http://localhost/api/)), and serve static files by itself (e.g., (http://localhost/static/client.html))


### Run the app as a service

Add the following file under `/etc/systemd/system/sweeper.service`.

```
[Unit]
Description=Minesweeper API
After=network.target

[Service]
Type=simple
ExecStart=/bin/bash /usr/sbin/sweeper-start.sh
ExecStop=/bin/bash /usr/sbin/sweeper-stop.sh
TimeoutStartSec=0
Restart=on-failure
RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=%n


[Install]
WantedBy=default.target
```

Add the following file under `/usr/sbin/sweeper-start.sh`.

```bash
#!/bin/bash

cd /home/dliberat/minesweeper-api # modify this to be the actual location of the source code
docker-compose -f docker-compose-prod.yml up
```

Give the file executable permissions:

```bash
sudo chmod +x sweeper-start.sh
```

Add the following file under `/usr/sbin/sweeper-stop.sh`.

```bash
#!/bin/bash

cd /home/ubuntu/minesweeper-api # modify this to be the actual location of the source code
docker-compose -f docker-compose-prod.yml down
```

And give the file executable permissions:

```bash
sudo chmod +x sweeper-stop.sh
```

Reload the systemctl daemon.

```bash
sudo systemctl daemon-reload
```

The service can now be started and stopped with `systemctl`.

```bash
sudo systemctl status sweeper
sudo systemctl start sweeper
sudo systemctl stop sweeper
sudo systemctl restart sweeper
sudo systemctl enable sweeper
```

Service logs can also be viewed:

```bash
journalctl -f -u sweeper.service
```


### TO DO:

- Set up CI/CD
