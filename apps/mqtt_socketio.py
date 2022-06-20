# -*- encoding: utf-8 -*-

import time
import json
from flask import request
from flask_mqtt import Mqtt
from flask_socketio import SocketIO, join_room, leave_room
from flask_apscheduler import APScheduler

import optparse
from geomet import wkt
# from .mapmatcher import MapMatcher
from datetime import datetime
import eventlet

eventlet.monkey_patch()

VEHICLE_ID = 'ANEV01'

def config_mqtt_socketio(app):
#    app.config['MQTT_BROKER_URL'] = '192.168.50.192'
#    app.config['MQTT_BROKER_PORT'] = 1883

    app.config['MQTT_BROKER_URL'] = '192.168.0.231'
    app.config['MQTT_BROKER_PORT'] = 9001
    app.config['MQTT_USERNAME'] = 'iauto'
    app.config['MQTT_PASSWORD'] = 'iauto'

    mqtt = Mqtt(app, connect_async=True)
    socketio = SocketIO(app)
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    # app.mapmatcher = MapMatcher('apps/fmm_config_XSP_TEP.json')

    app.vehicle = {}

    # MQTT part
    @mqtt.on_connect()
    def on_connect(client, userdata, flags, rc):
        mqtt.subscribe('#', qos=2)
        app.logger.info('connected')

    @mqtt.on_message()
    def om_message(client, userdata, message):
        # app.logger.info('Get topic: ' + message.topic)
        # app.logger.info(payload)

        # Try to loads Json-liked message
        try:
            payload = json.loads(message.payload.decode())
        except json.decoder.JSONDecodeError:
            app.logger.error(f"Json loads error ({message.topic}): {message.payload.decode()}")
            return None

        # Try to categorize topic name and corresponding callback
        try:
            main_field, sub_field = message.topic.split('/', 1)
            {
                'dashboard'    : __dashboard,
                'vehicle_info' : __vehicle_info,
            }.get(main_field, lambda *x: None)(sub_field, payload.copy())
        except ValueError:
            return None

    def __dashboard(sub_topic, payload):
        {
            'user_event': __dashboard__user_event,
            'dispatch_info': __dashboard__dispatch_info,
        }.get(sub_topic, lambda *x: None)(payload)

    def __dashboard__user_event(payload) -> None:
        pass

    def __dashboard__dispatch_info(payload) -> None:
        vehicle: dict = payload.get('vehicle').copy()
        uuid   : str  = payload.get('uuid')
        path   : dict = payload.get('path').copy()
        if vehicle and uuid and path:
            map_table: dict = {
                0: '任務結束',
                1: '東側出口',
                2: '夢想館',
                3: '北側出口',
                4: '台北玫瑰館',
                5: '兒童遊樂場',
            }
            vehicle_id: str  = vehicle['vehicle_id']
            if not app.vehicle.get(vehicle_id):
                app.vehicle[vehicle_id]: dict = {}

            app.vehicle[vehicle_id]['property']: PROPERTY = PROPERTY(platform = vehicle["platform"])

            begin = 'N/A'
            end = map_table.get(path['trip'])
            app.vehicle[vehicle_id]['trip'] = TRIP(
                timestamp = payload.get('timestamp', -1),
                uuid      = uuid,
                account   = path['account'],
                quantity  = path['number_of_people'],
                begin     = begin,
                end       = end,
            )
            path['vehicle_id'] = vehicle_id
            path['from'] = begin
            path['to']   = end
            socketio.emit('user_information',
                {
                    'vehicle_id': vehicle_id,
                    'account'   : path['account'],
                    'from'      : begin,
                    'to'        : end,
                    'number_of_people': path['number_of_people']
                },
                to = vehicle_id,
            )
        else:
            app.logger.error('Missing key(s) in dashboard/dispatch_info')

    def __vehicle_info(topic, payload):
        field_dispatcher = {
            'location'  : __vehicle_info__location,
            'state'     : __vehicle_info__state,
            'perception': __vehicle_info__perception,
        }

        vehicle_id, *_ = topic.split('/', 1)

        if not app.vehicle.get(vehicle_id):
            app.vehicle[vehicle_id] = {}

        for key, val in payload.items():
            field_dispatcher.get(key, lambda *x: None)(vehicle_id, val)

    max_count = 20
    counter = 0
    history_pts = [()] * max_count

    def __vehicle_info__location(vehicle_id, payload):
        nonlocal counter, history_pts

        app.vehicle[vehicle_id]['position'] = {
            'timestamp': datetime.now(),
            'data': LOCATION(
                longitude = payload.get('longitude',  0.0),
                latitude  = payload.get('latitude' ,  0.0),
                height    = payload.get('height'   , -1.0),
                speed     = payload.get('speed'    , -1.0),
                status    = payload.get('status'   , 'na'),
                geo_type  = payload.get('geo_type' , -1)
            )
        }

        # history_pts[counter] = (lng,lat)
        '''
        counter += 1

        if counter == max_count:
            counter = 0
            point = {
                'type': 'LineString',
                'coordinates': history_pts
            }

            result = app.mapmatcher.match_wkt(wkt.dumps(point, decimals = 6))
            mgeom_wkt = result.mgeom.export_wkt() if result.mgeom.get_num_points() > 0 else ''

            if mgeom_wkt:
                # app.logger.info(wkt.loads(mgeom_wkt))

                history_payload = wkt.loads(mgeom_wkt)
                socketio.emit('vehicle_history', history_payload)
            else:
                app.logger.warning("Map matching failed")
        '''

    def __vehicle_info__state(vehicle_id, payload):
        if not app.vehicle.get(vehicle_id):
            app.vehicle[vehicle_id] = {}

        app.vehicle[vehicle_id]['state'] = STATE(
            localization_state = payload.get('localization_state', False),
            up_mid_communication = payload.get('up_mid_communication', False),
            mid_bot_communication = payload.get('mid_bot_communication', False)
        )
        socketio.emit('vehicle_state',
            {
                "localization"    : app.vehicle[vehicle_id]['state'].localization_state,
                "upper_middle_com": app.vehicle[vehicle_id]['state'].up_mid_communication,
                "middle_lower_com":app.vehicle[vehicle_id]['state'].mid_bot_communication
            },
            to=vehicle_id
        )

    def __vehicle_info__perception(vehicle_id, payload):
        event_code = payload.get('obstacle_info')
        if event_code:
            event_list = [
               '',
               'Stop for more than 10 seconds after detecting an obstacle ahead',
               'Detecting an obstacle ahead that causes the ANEV to be slower than the preset speed for more than 10 seconds'
            ]
            try:
                event_str = event_list[event_code]
            except IndexError:
                event_str = f"Undefined event code: {event_code}"
            if len(event_str) != 0:
                # app.logger.warning(f"({event_code}) {event_str}")
                time = datetime.now().strftime("%Y-%d-%m %H:%M:%S")
                socketio.emit('vehicle_event', {'text': time + '\t' + event_str}, to=vehicle_id)

    @scheduler.task('interval', id='vehicle_info_update', seconds=1, misfire_grace_time=900)
    def __vehicle_info__update():
        payload_position = []
        for key, fields in app.vehicle.items():
            if fields.get('position'):
                t   = fields['position']['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
                veh = fields['position']['data']
                url = f'192.168.50.12:5005/iauto_dashboard/{key}.html'
                payload_position.append({
                    'label': '<br>'.join([t, key]),
                    'url': url,
                    'data': {
                        'type': 'Feature',
                        'properties': {
                            'name': key,
                            'popupContent': key,
                        },
                        'geometry': {
                            'type': 'Point',
                            'coordinates': [veh.longitude, veh.latitude],
                        }
                    }
                })
        socketio.emit('vehicle_position', payload_position)
        #app.logger.warning(app.vehicle)

    @mqtt.on_log()
    def on_log(client, userdata, level, buf):
        pass
        # app.logger.info(buf)

    # SocketIO part
    @socketio.on('join_monitor_room')
    def join_monitor_room(room):
        join_room(room, sid = request.sid)
#        app.logger.warning(f'{request.sid} join {room}')

    @socketio.on('leave_monitor_room')
    def join_monitor_room(room):
        leave_room(room, sid = request.sid)
#        app.logger.warning(f'{request.sid} leave {room}')

    @socketio.on('get_order_info')
    def get_order_info(vehicle_id):
        if vehicle_id and app.vehicle.get(vehicle_id):
            trip = app.vehicle[vehicle_id].get('trip')
            if trip:
                socketio.emit('user_information',
                    {
                        'vehicle_id': vehicle_id,
                        'account'   : trip.account,
                        'from'      : trip.begin,
                        'to'        : trip.end,
                        'number_of_people': trip.quantity,
                    },
                    to = vehicle_id,
                )

    @socketio.on('task-auth')
    def task_accept(payload):
        vehicle_id = payload['vehicle_id']
        acceptance = payload['auth']
        app.logger.info(f'{vehicle_id}: task ' + ('accepted' if acceptance else 'refused'))

        trip = app.vehicle.get(vehicle_id).get('trip', None)
        if trip is not None:
            payload = json.dumps({
                'timestamp': time.time(),
                'uuid': trip.uuid,
                'acceptance': acceptance,
            })
            mqtt.publish('dashboard/permission', payload)

        else:
            app.logger.error(f'Invalid vehicle id ({vehicle_id})')

    @socketio.on('vehicle-control')
    def vehicle_control(payload):
        app.logger.warning(request.sid)
        vehicle_id = payload['vehicle_id']
        command    = payload['command']
        app.logger.info('vehicle-control: ' + command)
        command_table = {
            'active': 'start',
            'stop': 'stop',
            'lane-change': 'lane_change'
        }
        control = command_table.get(command, None)
        if control is None:
            app.logger.warning('Unknown vehicle control command: ' + command)
            return None
        payload = json.dumps({
            'timestamp': time.time(),
            'control': {
                'command': control,
            }
        })
        mqtt.publish('route/' + vehicle_id, payload)


from dataclasses import dataclass
@dataclass
class PROPERTY:
    platform: str

@dataclass
class STATE:
    localization_state: bool
    up_mid_communication: bool
    mid_bot_communication: bool

@dataclass
class LOCATION:
    longitude: float
    latitude: float
    height: float
    speed: float
    status: str
    geo_type: int

@dataclass
class TRIP:
    timestamp: float
    uuid: str
    account: str
    quantity: int
    begin: str
    end: str
