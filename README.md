## How to install and run the app

### 1. start the docker container

### 2. start mysql server

```shell
cd docker

docker-compose up -d
```

### 3. start the app

```shell
cd ..

flask run
```

visit http://127.0.0.1/5000

### 4. monitor the logs

```shell
tail -f logs/app.log
```

after altering db models (models.py), run the following commands to update the database

```shell
flask db migrate -m "add deleted_at field to all tables"

flask db upgrade
```

# TODO

- [x] add reminder and send email by cron