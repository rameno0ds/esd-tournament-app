# Project Setup


## Set up backend
CD to backend and
```sh
docker compose up --build
```
This should build all our service containers. 
### !!!Important note!!!
The notification service requires a manual start. To do so, locate notification-service within the terminal and CMD + Click to send a GET request to http://0.0.0.0:8000

## Set up frontend

CD to frontend folder and 
```sh
npm install
```

## Run front end

```sh
npm run dev
```

