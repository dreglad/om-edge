# Open Multimedia Edge Server

Edge server for Open Multimedia HTTP services

## Usage

1. Set environment variables to configure services (see Docker Compose file for reference)
2. Run services:

  ```sh
  $ make run
  ```

* Restart edge server

 ```sh
  $ make restart
  ```

* Watch edge server logs

 ```sh
  $ make logs
  ```

## Services

  * admin-legacy
  * live2vod
  * images (image manipulation based on thumbor)
  * media (media files proxy)
  * live (public live streaming)
  * get (generic proxy)
