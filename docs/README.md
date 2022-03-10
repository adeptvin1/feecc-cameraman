# Feecc Cameraman

## Overview

Feecc Cameraman is a microservice, designed to record video from several RTSP streams simultaneously on demand.

It provides a simple REST API interface to start and end recordings, get information about attached cameras (RTSP
streams). It also handles user authentication.

Feecc Cameraman comes as a part of the Feecc QA system - a Web3 enabled quality control system.

Cameraman is a microservice that is written in asynchronous Python using FastAPI framework and relies on Ffmpeg to
record video streams.

## Deployment

The app is supposed to be run in a Docker container and can be configured by setting several environment variables.

> Note, that we assume a Linux host in this guide, however you can also run Cameraman on any other OS,
> but be warned: timezone is defined by mounting host `/etc/timezone` and `/etc/localtime` files inside the container,
> which are not present on Windows machines, so you might end up with UTC time inside your container.

Start by cloning the git repository onto your machine: `git clone https://github.com/Multi-Agent-io/feecc-cameraman.git`

Enter the app directory and modify the `docker-compose.yml` file to your needs by changing the environment variables
(discussed in the configuration part).

```
cd feecc-cameraman
vim docker-compose.yml
```

When you are done configuring your installation, build and start the container using docker-compose:
`sudo docker-compose up --build`

Verify your deployment by going to http://127.0.0.1:8081/docs in your browser. You should see the SwaggerUI API
specification page. Continue from there.

## Configuration

To configure your Cameraman deployment edit the environment variables, provided in `docker-compose.yml` file.

### Environment variables

- `MONGODB_URI` - Your MongoDB connection URI ending with `/db-name`
- `PRODUCTION_ENVIRONMENT` - Leave null if you want testing credentials to work, otherwise set it to `true`
- `CAMERAS_CONFIG` - A JSON-like string for camera configuration. This string represents a JSON list of strings, each
  one describing an RTSP stream ("-" separated stream number, stream socket and RTSP stream URI). Example:

  ```'["1-192.168.88.239:554-rtsp://login:password@192.168.88.239:554/Streaming/Channels/101"]'```
