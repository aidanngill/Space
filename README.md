# Space
Space for your files to live.

## Requirements
- Python 3.8
- SQL Database
- WSGI + Web Server

Your SQL database should be supported by SQLAlchemy. A list of currently supported databases can be found [here](https://docs.sqlalchemy.org/en/14/dialects/). [PostgreSQL (13.2)](https://www.postgresql.org/download/) was used during testing of Space.

Only Gunicorn and Nginx will be covered in the installation guide.

## Installation

0. Make a separate `space` user.

```bash
$ sudo adduser space
$ su space
$ cd ~
```

You must also make a new user for your database with the same name. For PostgreSQL, do the following. **Change `user_password_here` to a secure password**.

```
$ sudo -u postgres psql
psql=# CREATE DATABASE space;
psql=# CREATE USER space WITH ENCRYPTED PASSWORD 'user_password_here';
psql=# GRANT ALL PRIVILEGES ON DATABASE space TO space;
psql=# \q
```

1. Clone the repository to somewhere private, e.g. not exposed on a web server.

```bash
$ cd /home/space
$ git clone https://github.com/ramadan8/Space
$ cd space
```

2. Create a virtual environment and install the requirements.

```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ python3 -m pip install -r requirements.txt
```

3. Add the environment variables to the `.env` file.

```bash
$ nano .env
```

| Name | Description | Required | Example |
| ---- | ----------- | -------- | ------- |
| `APPLICATION_NAME` | Name of the application, shown on frontend and configs. | ✗ | `Space` |
| `DATABASE_URI` | The URI of the database. | ✗ | `postgresql://space:user_password_here@localhost/space` |
| `SECRET_KEY` | Secret key used for Flask. Treat this like a password. | ✓ | `BdIJ9J8B3SI7%NJU` |
| `RECAPTCHA_ENABLED` | Whether or not Google's reCAPTCHA should be used. | ✗ | `true` |
| `RECAPTCHA_PUBLIC_KEY` | Google reCAPTCHA public key. | ✓ (if `RECAPTCHA_ENABLED`) | `your_public_key` |
| `RECAPTCHA_PRIVATE_KEY` | Google reCAPTCHA private key. | ✓ (if `RECAPTCHA_ENABLED`) | `your_private_key` |
| `UPLOAD_FOLDER` | Where to save files to. | ✗ | `/var/www/files/` |
| `FILE_UPLOAD_BASE` | URL where files will be served from. | ✓ | `https://example.com/uploads` |
| `API_URL_BASE` | Base URL for the API. | ✓ | `https://api.example.com` |

4. Upgrade the database.

```bash
$ flask db migrate
$ flask db upgrade
```

5. Add the service provided in `space.service`.

```bash
$ sudo cp space.service /etc/systemd/system/space.service
$ sudo systemctl enable space.service
$ sudo systemctl start space.service
```

**The next step is only necessary if you are using Gunicorn with Nginx specifically.**

6. Add the Nginx site provided in `nginx.conf`.

```bash
$ sudo cp nginx.conf /etc/nginx/sites-available/space.conf
$ sudo ln -s /etc/nginx/sites-available/space.conf /etc/nginx/sites-enabled/
$ sudo nginx -t
$ sudo systemctl restart nginx
```

The file host should now be running on `http://localhost`. To change the host name, simply adjust the `space.conf` file in `/etc/nginx/sites-available/`.