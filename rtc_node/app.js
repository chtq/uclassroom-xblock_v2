var express = require('express');
var fs = require('fs');
var http = require('http');
var colors = require('colors');
var sio = require('socket.io');

var util = require('./util.js');
var config = JSON.parse(fs.readFileSync('./config.json'));
var app = express();

var USERS = [];
var ROOMS = [];

function removeRoom(room_id) {
	var index = getRoomIndex(room_id);
	if (index >= 0) {
		ROOMS.splice(index, 1);
	}
}

function getRoom(room_id) {
	var index = getRoomIndex(room_id);
	if (index >= 0) {
		return ROOMS[index];
	}
	return { };
}

function getRoomIndex(room_id) {
	for (var i = 0; i < ROOMS.length; i++) {
		if (ROOMS[i].id == room_id) {
			return i;
		}
	}
	return -1;
}

function removeUser(user_id) {
	var index = getUserIndex(user_id);
	if (index >= 0) {
		USERS.splice(index, 1);
	}
}

function getUser(user_id) {
	var index = getUserIndex(user_id);
	if (index >= 0) {
		return USERS[index];
	}
	return { };
}

function getUserIndex(user_id) {
	for (var i = 0; i < USERS.length; i++) {
		if (USERS[i].id === user_id) {
			return i;
		}
	}
	return -1;
}

function getUsersInRoom(room_id) {
	if (room_id) {
		var tmpUsers = [];
		for (var i = 0; i < USERS.length; i++) {
			if (USERS[i].classroom.id === room_id) {
				tmpUsers.push(USERS[i]);
			}
		}
		return tmpUsers;
	}
	return USERS;
}

function log(message) {
	console.log(">>> " + message);
}

var server = http.createServer(app);
server.listen(config.PORT);
var io = sio.listen(server);
console.log('[info] '.green + 'start listening on port ' + config.PORT);
var nsp = io.of('/classroom');
nsp.on('connection', function(socket) {
    console.log('socket on [connection]'.blue);

    var user = {
		id: socket.id,  //here, user id is socket id, make emitting easier
		classroom: {},
		name: '',
		color: '',
        cameraSharing: false,
        microphoneSharing: false,
        screenSharing: false
	};
    USERS.push(user);

    // Bind user info
	socket.on('bind', function(message){
	    user.name = message.username;
	    socket.emit('bind', user);
	});


    // List rooms.
    socket.on('rooms', function() {
        socket.emit('rooms', ROOMS);
    });

    // Create room.
    // message.name      => room name
    // message.password  => room password, for future use
    // message.creator   => room creator
    socket.on('create_room', function(message) {
        console.log('socket on [create_room]'.blue);

        if (!util.isEmpty(user.classroom)) {
            var rMessage = {
                result: false,
                text: 'Please exit from other one before creating classroom.',
                room: { }
            };
            socket.emit('create_room', rMessage);
            return;
        }

        var room = {};
        room.id = util.createLongId();
        room.name = message.name;
        room.password = message.password;
        room.creator = message.creator;
        room.creatingTime = new Date();

        ROOMS.push(room);

        var rMessage = {
            result: true,
            text: '',
            room: room
        };
        socket.emit('create_room', rMessage);
        nsp.emit('rooms', ROOMS);  // Tell all to refresh rooms list
    });

    // Join room.
    // message.roomid  => room id
    socket.on('join_room', function(message) {
        console.log('socket on [join_room]'.blue);

        if (!util.isEmpty(user.classroom)) {
            if (message.roomid !== user.classroom.id) {
                var rMessage = {
                    result: false,
                    text: 'Please exit from other one before creating classroom.',
                    room: { }
                };
                socket.emit('join_room', rMessage);
            }
            else {
                var rMessage = {
                    result: false,
                    text: 'You have joined this room.',
                    room: { }
                };
                socket.emit('join_room', rMessage);
            }
            return;
        }

        var result_users = getUsersInRoom(message.roomid);
        if (result_users.length >= config.MAX_USER_NUM_OF_ROOM) {
            var rMessage = {
                result: false,
                text: 'The user number of the room has reached the maximum.',
                room: { }
            };
            socket.emit('join_room', rMessage);
        }
        else {
            var result_room = getRoom(message.roomid);
            user.classroom = result_room;
            var rMessage = {
                result: true,
                text: '',
                room: result_room
            };
            socket.emit('join_room', rMessage);
            socket.join(message.roomid);
            // Tell all in the room to refresh users list.
            result_users.push(user);
            nsp.in(message.roomid).emit('users', result_users);
        }
    });

    // Leave room.
    socket.on('leave_room', function() {
        console.log('socket on [leave_room]'.blue);

        if (util.isEmpty(user.classroom)) {
            var rMessage = {
                result: false,
                text: 'You have not joined any classroom.',
                closed: false
            };
            socket.emit('leave_room', rMessage);
            return;
        }

        socket.leave(user.classroom.id);
        var room = user.classroom;
        user.classroom = {};
        var users = getUsersInRoom(room.id);
        if (users.length == 0) {
            // Nobody is in room
            removeRoom(room.id);
            nsp.emit('rooms', ROOMS);
            var rMessage = {
                result: true,
                text: '',
                closed: true
            };
            socket.emit('leave_room', rMessage);
        }
        else {
            // Tell other users in room to refresh users list
            nsp.in(room.id).emit('users', users);
            var rMessage = {
                result: true,
                text: '',
                closed: false
            };
            socket.emit('leave_room', rMessage);
        }
    });

    // Disconnect server.
    socket.on('disconnect', function () {
        console.log('socket on [disconnect]'.blue);

        if (util.isEmpty(user.classroom)) {
            removeUser(user.id);
            return;
        }

        var room = user.classroom;
        socket.leave(user.classroom.id);

        removeUser(user.id);
        var users = getUsersInRoom(room.id);
        if (users.length == 0) {
            // Nobody is in room
            removeRoom(room.id);
            nsp.emit('rooms', ROOMS);
        }
        else {
            // Tell other users in room to refresh users list
            nsp.in(room.id).emit('users', users);
        }
    });

    // List users in room.
    // message.roomid => room id
    socket.on('users', function(message) {
        console.log('socket on [users]');
        socket.emit('users', getUsersInRoom(message.roomid));
    });

    // Receive text message.
    // message.text => text
    socket.on('text_message', function(message) {
        console.log('socket on [text_message]');

        if (util.isEmpty(user.classroom)) {
            var rMessage = {
                result: false,
                time: util.getTime(),
                from: '',
                text: 'no room'
            };
            socket.emit('text_message', rMessage);
            return;
        }

        var msg = {
            text: message.text,
            room: user.classroom,
            sender: user,
            time: util.getTime()
        };
        var rMessage = {
            result: true,
            time: msg.time,
            from: user.name,
            text: msg.text
        };
        // Send to all in the room
        nsp.in(user.classroom.id).emit('text_message', rMessage);
    });

    // Call for another's video/audio.
    // message.offer      => offer's id
    // message.answer     => answer's id
    // message.streamtype => 1.cam & mic; 2.screen; 3.screen & cam & mic
    socket.on('call', function(message) {
        console.log('socket on [call]'.blue);
        nsp.connected[message.offer].emit('call', message);
    });

    // Transfer candidate.
    // message.from  => from whom
    // message.to    => to whom
    // message.candidate
    // message.streamtype
    // tag => true:offer's candidate; false:answer's candidate
    socket.on('candidate', function(message) {
        console.log('socket on [candidate]'.blue);
        nsp.connected[message.to].emit('candidate', message);
    });

    // P2P answer.
    // message.sdp    => answer's sdp
    // message.offer  => offer's id
    // message.answer => answer's id
    // message.streamtype
    socket.on('answer', function(message) {
        console.log('socket on [answer]'.blue);
        nsp.connected[message.offer].emit('answer', message);
    });

    // P2P offer.
    // message.sdp    => sdp
    // message.offer  => offer's id
    // message.answer => answer's id
    // message.streamtype
    socket.on('offer', function(message) {
        console.log('socket on [offer]'.blue);
        nsp.connected[message.answer].emit('offer', message);
    });

    // Change user device sharing status.
    // message.userid =>
    // message.cameraSharing => true, false
    // message.microphoneSharing => true, false
    socket.on('share_cam', function(message) {
        user.cameraSharing = message.cameraSharing;
        user.microphoneSharing = message.microphoneSharing;
        var rMessage = {
            cameraSharing:  message.cameraSharing,
            microphoneSharing: message.microphoneSharing,
            userid: message.userid,
            username: user.name
        };
        nsp.in(user.classroom.id).emit('share_cam', rMessage); // in room
    });

    // Change user device sharing status.
    // message.userid =>
    // message.screenSharing => true, false
    socket.on('share_screen', function(message) {
        user.screenSharing = message.screenSharing;
        var rMessage = {
            screenSharing: message.screenSharing,
            userid: message.userid,
            username: user.name
        };
        nsp.in(user.classroom.id).emit('share_screen', rMessage); // in room
    });

});