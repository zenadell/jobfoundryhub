# 🚀 Deployment Commands for dozzy-site

Follow these commands on your Ubuntu 22.04 VPS.

## 2. & 3. Install Dependencies
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib nginx certbot python3-certbot-nginx
```

## 4. Clone and Setup Environment
```bash
# Clone the repository
git clone <your-repo-url> /var/www/dozzy-site
cd /var/www/dozzy-site

# Create virtualenv
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements/base.txt
pip install gunicorn psycopg2-binary
```

## 5. Environment Variables
Create the `.env` file:
```bash
cp .env.example .env
nano .env
# Update SECRET_KEY, ALLOWED_HOSTS, and DATABASE_URL
```

## 6. PostgreSQL Setup
```bash
sudo -u postgres psql
# In psql:
CREATE DATABASE dozzy_db;
CREATE USER dozzy_user WITH PASSWORD 'your_secure_password';
ALTER ROLE dozzy_user SET client_encoding TO 'utf8';
ALTER ROLE dozzy_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE dozzy_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE dozzy_db TO dozzy_user;
\q

# Update .env DATABASE_URL:
# DATABASE_URL=postgres://dozzy_user:your_secure_password@localhost:5432/dozzy_db
```

## 7. - 11. Django Operations
```bash
python manage.py migrate
python manage.py seed_data
python manage.py load_initial_blog_posts
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## 12. Nginx & Gunicorn
Copy the configuration files (provided in /deploy) to the system:
```bash
sudo cp deploy/gunicorn.socket /etc/systemd/system/
sudo cp deploy/gunicorn.service /etc/systemd/system/
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket

sudo cp deploy/dozzy_site.nginx /etc/nginx/sites-available/dozzy_site
sudo ln -s /etc/nginx/sites-available/dozzy_site /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## 13. SSL with Certbot
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```
