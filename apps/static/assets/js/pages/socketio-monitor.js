$(document).ready(function() {
    //var videoTag = $('video').get(0);
    //videoTag.addEventListener("loadedmetadata", function(event) {
    //    videoRatio = videoTag.videoWidth / videoTag.videoHeight;
    //    targetRatio = $(videoTag).width() / $(videoTag).height();
    //    if (videoRatio < targetRatio) {
    //       $(videoTag).css("transform", "scaleX(" + (targetRatio / videoRatio) + ")");
    //    } else if (targetRatio < videoRatio) {
    //        $(videoTag).css("transform", "scaleY(" + (videoRatio / targetRatio) + ")");
    //    } else {
    //         $(videoTag).css("transform", "");
    //    }
    //});

    console.log('Connect to ' + 'http://' + document.domain + ':' + location.port);
    var socket = io.connect('http://' + document.domain + ':' + location.port);


    socket.on('connect', function(socket_) {
        // console.log('hello');
        socket.emit('join_monitor_room', $('#user-vehicle').val());
        socket.emit('get_order_info', $('#user-vehicle').val());
    });
    socket.on('disconnect', function(reason) {
        console.log('bye~');
        socket.emit('leave_monitor_room', $('#user-vehicle').val());
    });

    socket.on('order_information', function(data) {
        // console.log(data);
        // var text = '(' + data['topic'] + ' qos: ' + data['qos'] + ') ' + data['payload'];
        // $('#subscribe_messages').append(text + '<br><br>');
    });
    socket.on('user_information', function(data) {
        // console.log(data);

        $('#user-vehicle').val(data.vehicle_id);
        $('#user-name').val(data.account);
        $('#user-from').val(data.from);
        $('#user-to').val(data.to);
        $('#user-quantity').val(data.number_of_people);
    });

    socket.on('vehicle_state', function(data) {
        // console.log(data);
        function get_type(state_type) {
            if (state_type == 1) return 'spinner-grow text-success';
            if (state_type == 0) return 'spinner-grow text-danger';
            return 'spinner-grow text-dark';
        };
        $('#state-position').removeClass().addClass(get_type(data.localization));
        $('#state-upper-middle-com').removeClass().addClass(get_type(data.upper_middle_com));
        $('#state-middle-lower-com').removeClass().addClass(get_type(data.middle_lower_com));
    });

    socket.on('vehicle_event', function(data) {
        // console.log(data);
        $('#event-card').prepend(`
            <div class='alert alert-danger alert-dismissible fade show' role='alert'>
               <strong>${data.text}</strong>
               <button type='button' class='close' data-dismiss='alert' aria-label='Close'><span aria-hidden='true'>×</span></button>
            </div>
        `);
    });

    // Button events
    $('#btn-task-accept').on('click', function(event) {
        socket.emit('task-auth', {'vehicle_id': $('#user-vehicle').val(), 'auth': true});
    });
    $('#btn-task-refuse').on('click', function(event) {
        socket.emit('task-auth', {'vehicle_id': $('#user-vehicle').val(), 'auth': false});
    });
    $('#btn-active').on('click', function(event) {
        socket.emit('vehicle-control', {'vehicle_id': $('#user-vehicle').val(), 'command': 'active'});
    });
    $('#btn-stop').on('click', function(event) {
        socket.emit('vehicle-control', {'vehicle_id': $('#user-vehicle').val(), 'command': 'stop'});
    });
    $('#btn-lane-change').on('click', function(event) {
        socket.emit('vehicle-control', {'vehicle_id': $('#user-vehicle').val(), 'command': 'lane-change'});
    });
});
