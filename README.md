<h1 align="center">
    <img alt="NOCELLOS" src="https://user-images.githubusercontent.com/76264011/201493757-10049ba6-0f4f-49d2-a07e-72b01ed8900d.png" width="300px" horizontal-align="center">
</h1>

## Overview  

Nocellos is a flash-card app made by a group of three students for the Ventspils IT Challenge.  
The idea of the app is to allow for students to organize their notes and review them more effectively.
They can invite their friends/classmates and create common study sets, helping each other. 
There they can also view each other's progress and compete with each other on the leaderboard each week  
You can visit the website here: [nocellos.vercel.app](https://nocellos.vercel.app/)  
Designs on Figma: [Here](https://www.figma.com/file/Gh1fpY8fzGORZKxYOMiHqc/Nocellos?node-id=0%3A1&t=ZhGc7fMdFSgBHyz6-1)

## Setup locally  

### Tools used

<img display="inline-block" alt="Next.js" src="https://user-images.githubusercontent.com/76264011/201494824-b8bedfaf-0434-4dcc-a9e2-8bf047c34ba3.png" width="50px" height="50px"><img display="inline-block" alt="Tailwind" src="https://user-images.githubusercontent.com/76264011/201494945-f962dd4e-ef3f-4450-9ebe-ba99a512050e.png" width="50px" height="50px">
<img display="inline-block" alt="FastAPI" src="https://raw.githubusercontent.com/devicons/devicon/1119b9f84c0290e0f0b38982099a2bd027a48bf1/icons/fastapi/fastapi-plain.svg" width="50px" height="50px">
<img display="inline-block" alt="PostgreSQL" src="https://github.com/devicons/devicon/raw/master/icons/postgresql/postgresql-plain-wordmark.svg" width="50px" height="50px">

### Clone repository  

```shell
git clone https://github.com/theglobehead/nocellos.git
```

### Run api  

```shell
docker-compose up api
```

#### Environment variables  

| Variable name  |                     Value                      |
|----------------|:----------------------------------------------:|
| DB_HOST        |  the host address for the postgresql database  |
| DB_NAME        |            The name of the database            |
| DB_PASSWORD    |      Password for accessing the database       |
| DB_USER        |           Name of the database user            |
| EMAIL_PASSWORD |         The app password for the email         |
| SERVER_NAME    | Address of the server where the site is hosted |
| PORT           |       The port on which the API listens        |

### Run frontend  

```shell
nx serve www
```
