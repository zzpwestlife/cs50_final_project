# An easy-to-use to-do list app

## Video Demo

https://www.youtube.com/watch?v=itH9fyQk2_g

## Description

This is a simple to-do list app. It is built with Flask, MySQL, and Docker.

## Features

- [x] User can register and login
- [x] User can create, update, and delete a task
- [x] User can mark a task as completed
- [x] User can view all uncompleted tasks
- [x] User can view all tasks created by him/herself
- [x] If deadline is set, user will receive an email notification when the deadline is approaching

attention: 
- [x] User can only login with a valid username and password
- [x] User can only register with a unique username and password
- [x] User can only update/delete his/her own tasks
- [x] User can only mark his/her own tasks as completed
- [x] User can only view his/her own uncompleted tasks
- [x] The email will only be sent to the user once

# How to install and run the app

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

and visit http://127.0.0.1/5000
