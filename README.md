## Compose sample application
### Python/Flask application

Project structure:
```
.
├── docker-compose.yaml
├── app
    ├── Dockerfile
    ├── requirements.txt
    └── app.py

```

[_docker-compose.yaml_](docker-compose.yaml)
```
services: 
  web: 
    build: app 
    ports: 
      - '5000:5000'
```
## Run some tests
```
python -m pytest
```

## Build docker image

```
$  docker build -t blacklist_service .
```


## Deploy with docker-compose

```
$ docker-compose up -d
  blacklist_service  main  docker-compose up -d
[+] Running 2/2
 ⠿ Container mongo      Started                               1.0s
 ⠿ Container blacklist  Started                               0.5s
```

## Expected result

Listing containers must show one container running and the port mapping as below:
```
$ docker ps
CONTAINER ID   IMAGE                      COMMAND                  CREATED         STATUS              PORTS                      NAMES
7c53625a2904   blacklist_service:latest   "python app.py"          2 minutes ago   Up About a minute   0.0.0.0:5000->5000/tcp     blacklist
b1891791ea61   mongo:5.0.4                "docker-entrypoint.s…"   2 minutes ago   Up About a minute   0.0.0.0:27017->27017/tcp   mongo
```

## After the application starts

Not what you would want in a production server, add test data to mongo navigate to `http://localhost:5000/add_test_data` in your web browser or run:
```
$ curl localhost:5000/add_test_data
status	200
success	true

```

To begin testing urls:
```
$ curl localhost:5000/urlinfo/1/www.sfu.ca/about/economic-recovery/1-10.html
status	200
success	false
```

Test URLs:

* www.sfu.ca/about/economic-recovery/1-10.html
* ubc.ca/academics/
* umbrella.cisco.com/?dtid=osscdc000283
* www.geeksforgeeks.org:443/python-build-a-rest-api-using-flask/

Encoded Versions store in Mongo:
* www.sfu.ca%2Fabout%2Feconomic-recovery%2F1-10.html
* ubc.ca%2Facademics%2F
* umbrella.cisco.com%2F%3Fdtid%3Dosscdc000283
* www.geeksforgeeks.org%3A443%2Fpython-build-a-rest-api-using-flask%2F


Stop and remove the containers
```
$ docker-compose down
```
