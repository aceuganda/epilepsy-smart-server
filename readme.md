# Flask API Template

This project is aimed at creating the EPILEPSY SMART SERVER flask restful api.



## Project Setup

Follow these steps to have a local running copy of the app.

### Clone The Repo

`git clone https://github.com/aceuganda/epilepsy-smart-server.git`

If `main` is not up to date, `git checkout develop`. However, note that code on develop could be having some minor issues to sort.

### Install PostgreSQL

Here's a great resource to check out:

[How To Install and Use PostgreSQL](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-18-04)

Create a development database and call it `epilepsy_smart_db`.

### Create a Virtual Environment

create virtual enviroment called venv

Run `virtualenv venv`

### Activate the virtual environment

Run `. venv/bin/activate`

Make sure you have `pip` installed on your machine.

### Install the dependencies

```bash
pip install -r requirements.txt
```

### Create a .env file

Create a `.env` file (which defines the environment variables used) at the root of the app. You can create it by renaming example.env 

Add the following details, customizing as needed.

```bash
export FLASK_APP=server.py
export DATABASE_URI=postgresql:///flask_app_db
export FLASK_APP_SECRET=qY2i691SX2sEuZ7LUjY480RS48mw5qCeUiyV0i0vzmg
export FLASK_ENV=development
export FLASK_RUN_PORT=5000
```

### Run Database migrations

Run migrations for the database. This will create the tables for the models in the database .

`python manage.py db upgrade`

#### Note:
If you make changes to the models, you need to create migrations for the changes by running `python manage.py db migrate` and then `python manage.py db upgrade` to add the changes to the database.


##### Creating default roles

To create the default roles

`python manage.py create_roles`

##### Creating default admin account

To create an admin account run

`python manage.py admin_user --email=<an email> --password=<the password> --confirm_password=<the password>`

### Run Application

Run the application with this command

```bash
flask run
```

### Test the API

Through your browser go to link `localhost:<flask_port>/`.

### Checkout Application Api docs

Through your browser go to link `localhost:<flask_port>/apidocs`.
