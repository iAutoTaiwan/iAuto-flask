# Change Log

## [1.0.0] 2022-06-20
### Initial Release

- Add features
  - Coupled to gradient template
    - In `run.py`
      - Import `mqtt_socketio.py`
      - Change web server to SocketIO server
    - Static vehicle URL routing in `routes.py`
  - Isolated
    - Integrate core module `mqtt_socketio.py`
    - WebRTC streaming
      - JS: adapter.min.js, webrtchandler.js, webrtcstreamer.js
      - CSS: webrtc.css, webrtc-styles.css
    - SocketIO real-time interaction
      - JS: socketio-map.js, socketio-monitor.js
    - Add FMM git submodule
    - (Incomplete) Trajectory map matching using FMM
      - Example: XSP_TEP_data
      - Core python module: mapmatcher.py, fmm_config_XSP_TEP.json
      - JS: initial_mapbox_XSP_TEP.js, boundary_mapbox_XSP_TEP.js

- Add / Change layout
  - sidebar.html
    - Add Dashboard and Map tag
  - iauto_dashboard.html, iauto_map.html
    - New html template

- Change configuration
  - File `gunicorn-cfg.py`
    - Add `worker_class` to use SocketIO
  - File `nginx/appseed-app.conf`
    - Add SocketIO configuration but test failed, change preserved

- Add excutable files to easily run program
  - run.exe to start web server
  - webRTC_docker.ext to run webrtc-streamer

- Add packages in `requirements.tx`
  - eventlet = 0.30.2 for eventlet task management
  - flask_mqtt to support MQTT
  - flask_socketio to support SocketIO
  - flask_apscheduler to support task scheduling
