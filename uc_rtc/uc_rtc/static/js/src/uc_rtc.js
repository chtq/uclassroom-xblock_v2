'use strict';
var rtc;
var SOCKET_IO_NSP = SOCKET_IO_URL + '/classroom';

/* Javascript for UcRtcXBlock. */
function UcRtcXBlock(runtime, element) {

    var getNameHandleUrl = runtime.handlerUrl(element, 'get_name');

    $(function ($) {
        /* Here's where you'd do things on page load. */

        rtc = new init_rtc_socket();

        $.ajax({
            type: "POST",
            url: getNameHandleUrl,
            data: JSON.stringify({}),
            success: getNameCallback
        });
    });

    function getNameCallback(result) {
        var studentName = result.username;
        if (rtc != null) {
            rtc.socket.emit('bind', {username: studentName});
        }
    }
}

function init_rtc_socket() {

    var that = this;
    var user;
    var isCamSharing = false, isScreenSharing = false;
    var mediaStream, screenStream;
    var remoteCameraStream, remoteScreenStream;
    var rtcPeerConnections = { };

    var iceServers = (navigator.mozGetUserMedia) ?
      { iceServers:[{ url: 'stun:23.21.150.121'}] } : // number IP
      { iceServers: [{ url: 'stun:stun.l.google.com:19302'}] };
    var optionalRtpDataChannels = {
        optional: [
            { RtpDataChannels: true },
            { DtlsSrtpKeyAgreement: true }
        ]
    };
    var audioOnlyOfferConstraints = {
        optional: [],
        mandatory: {
            OfferToReceiveAudio: true,
            OfferToReceiveVideo: false
        }
    };
    var videoOnlyOfferConstraints = {
        optional: [],
        mandatory: {
            OfferToReceiveAudio: false,
            OfferToReceiveVideo: true
        }
    };
    var offerConstraints = {
        optional: [],
        mandatory: {
            OfferToReceiveAudio: true,
            OfferToReceiveVideo: true
        }
    };

    //--------SOCKET.IO--------
    this.socket = io.connect(SOCKET_IO_NSP);
    console.log(SOCKET_IO_NSP);
    this.socket.on('connect', function(session_user) {
        console.log('socket on connect');
        // Wait for XBlock to get student name, so "bind-emit" should be called by XBlock
        //that.socket.emit('bind', {username: studentName});
    });
    this.socket.on('bind', function(session_user) {
        console.log('bind userid:' + session_user.id);
        user = session_user;
        that.socket.emit('rooms');
    });
    this.socket.on('rooms', function(rooms) {
        console.log('socket on rooms');

        refreshRoomListDOM(rooms);
    });
    this.socket.on('create_room', function(message) {
        console.log('socket on create_room');

        if (message.result) {
            that.joinRoom(message.room.id);
        }
        else {
            alert(message.text);
        }
    });
    this.socket.on('join_room', function(message) {
        console.log('socket on join_room');

        if (message.result) {
            refreshRoomDOM(message.room);
        }
        else {
            alert(message.text);
        }
    });
    this.socket.on('leave_room', function(message) {
        console.log('socket on leave_room');

        if (message.result) {
            refreshRoomDOM(false);
        }
        else {
            alert(message.text);
        }
    });
    this.socket.on('users', function(users) {
        console.log('socket on users');

        refreshUserListDOM(users);
    });
    this.socket.on('text_message', function(message) {
        console.log('socket on text_message');

        if (message.result) {
            refreshMessageListDOM(message.time, message.from, message.text, 'White');
            messageInput.value = '';
        }
        else {
            refreshMessageListDOM(message.time, 'Cannot send message.',  message.text, 'Yellow');
        }
    });
    this.socket.on('share_cam', function(message) {
        console.log('socket on [share_cam]');
        refreshUserDeviceDOM(message.userid, message.username, message.cameraSharing, message.microphoneSharing);
    });
    this.socket.on('share_screen', function(message) {
        console.log('socket on [share_screen]');
        refreshUserDeviceDOM(message.userid, message.username, '', '', message.screenSharing);
    });
    // call for sharing
    // offer
    // answer
    // streamtype => 1.camera, 2.microphone, 3.cam & mic, 4.screen
    this.socket.on('call', function(message) {
        console.log('socket on [call]');

        if (message.streamtype === 1 || message.streamtype === 2 || message.streamtype === 3) {
            if (!mediaStream) {
                console.log('no media stream');
                return;
            }
            rtcPeerConnections[message.answer + '-offer-media'] = buildRtcPeerConnection(message.answer, message.streamtype, true);
            rtcPeerConnections[message.answer + '-offer-media'].addStream(mediaStream);
            switch (message.streamtype) {
                case 1:
                    rtcPeerConnections[message.answer + '-offer-media'].createOffer(rtcPeerConnections[message.answer + '-offer-media'].onoffercreated, onError, videoOnlyOfferConstraints);
                    break;
                case 2:
                    rtcPeerConnections[message.answer + '-offer-media'].createOffer(rtcPeerConnections[message.answer + '-offer-media'].onoffercreated, onError, audioOnlyOfferConstraints);
                    break;
                case 3:
                    rtcPeerConnections[message.answer + '-offer-media'].createOffer(rtcPeerConnections[message.answer + '-offer-media'].onoffercreated, onError, offerConstraints);
                    break;
            }
        }
        else if (message.streamtype === 4) {
            if (!screenStream) {
                console.log('no screen stream');
                return;
            }
            rtcPeerConnections[message.answer + '-offer-screen'] = buildRtcPeerConnection(message.answer, message.streamtype, true);
            rtcPeerConnections[message.answer + '-offer-screen'].addStream(screenStream);
            rtcPeerConnections[message.answer + '-offer-screen'].createOffer(rtcPeerConnections[message.answer + '-offer-screen'].onoffercreated, onError, videoOnlyOfferConstraints);
        }
        else {
            console.log('message.streamtype (' + message.streamtype + ') is wrong');
        }
    });
    // offer
    // answer
    // sdp
    // streamtype
    this.socket.on('offer', function(message) {
        console.log('socket on [offer]');
        var rtcPeerConnection = getRTCPeerConnection(message.offer, message.streamtype, false);
        console.log('setRemoteDescription');
        rtcPeerConnection.setRemoteDescription(new RTCSessionDescription(message.sdp), rtcPeerConnection.onremotesdpset, onError);
    });
    // offer
    // answer
    // sdp
    // streamtype
    this.socket.on('answer', function(message) {
        console.log('socket on [answer]');
        var rtcPeerConnection = getRTCPeerConnection(message.answer, message.streamtype, true);
        console.log('setRemoteDescription');
        rtcPeerConnection.setRemoteDescription(new RTCSessionDescription(message.sdp));
    });
    // from
    // to
    // candidate
    // streamtype
    // tag
    this.socket.on('candidate', function(message) {
        console.log('socket on [candidate]');
        var candidate = new RTCIceCandidate({
            sdpMLineIndex: message.candidate.sdpMLineIndex,
            candidate: message.candidate.candidate
        });
        getRTCPeerConnection(message.from, message.streamtype, !message.tag).addIceCandidate(candidate);
    });


    //--------CLASSROOM--------
    function createRoom() {
        console.log('function [createRoom]');
        var room = {
            name: roomNameInput.value,
            password: '',
            creator: user
        };
        that.socket.emit('create_room', room);
    }
    this.joinRoom = function(roomid) {
        console.log('function [joinRoom]');
        var room = {
            'roomid': roomid
        };
        that.socket.emit('join_room', room);
    }
    function leaveRoom() {
        console.log('function [leaveRoom]');
        if (mediaStream) { mediaStream.stop(); }
        if (screenStream) { screenStream.stop(); }
        if (remoteCameraStream) { remoteCameraStream.stop(); }
        if (remoteScreenStream) { remoteScreenStream.stop(); }
        //console.log('send socket message: leaveroom');
        that.socket.emit('leave_room');
    }
    function getUsers(roomid) {
        console.log('function [getUsers]');
        var message = { 'roomid': roomid };
        that.socket.emit('users', message);
    }
    function closingWindow() {
        return 'Confirm';
    }

    //--------USER MEDIA--------
    function shareCam() {
        if (isCamSharing === false) {
            initCamera();
        }
        else {
            stopSharingCamera();
        }
    }
    function shareScreen() {
        if (isScreenSharing === false) {
            initScreen();
        }
        else {
            stopSharingScreen();
        }
    }
    function initCamera() {
        var camConstraints = {
            audio: {
                optional: [],
                mandatory: {
                    //googEchoCancellation: true
                    //"googAutoGainControl": "false",
                    //"googNoiseSuppression": "false",
                    //"googHighpassFilter": "false"
                }
            },
            video: {
                mandatory: {
                    maxWidth: camWidthInput.value || 640,
                    maxHeight: camHeightInput.value || 360
                },
                optional: []
            }
        };
        getUserMedia(camConstraints, gotCamera, gotCameraError);
    }
    function initScreen() {
        var screenConstraints = {
            audio: false, //after 100 years, if Chrome supports sharing desktop with audio, set true
            video: {
                mandatory: {
                    chromeMediaSource: 'screen',
                    maxWidth: scrWidthInput.value || 1280,
                    maxHeight: scrHeightInput.value || 720
                },
                optional: [ ]
            }
        };
        getUserMedia(screenConstraints, gotScreen, gotScreenError);
    }
    function gotCamera(stream) {
        //console.log('gotCamera');
        attachMediaStream(localCam, stream);
        mediaStream = stream;
        isCamSharing = true;
        shareCamButton.innerHTML = 'StopSharingCam';
        var rMessage = {
            userid: user.id,
            cameraSharing: true,
            microphoneSharing: true
        };
        console.log('send sharecam message');
        that.socket.emit('share_cam', rMessage);
    }
    function gotCameraError(error) {
        //console.log('gotCameraError');
        alert('got Camera Error');
        stopSharingCamera();
    }
    function gotScreen(stream) {
        //console.log('gotScreen');
        attachMediaStream(localScr, stream);
        screenStream = stream;
        isScreenSharing = true;
        shareScreenButton.innerHTML = 'StopSharingScreen';
        var rMessage = {
            userid: user.id,
            screenSharing: true
        };
        console.log('send sharescreen message');
        that.socket.emit('share_screen', rMessage);
    }
    function gotScreenError(error) {
        //console.log('gotScreenError');
        alert('gotScreenError');
        stopSharingScreen();
    }
    function stopSharingCamera() {
        if (mediaStream) {
            mediaStream.stop();
        }
        mediaStream = null;
        isCamSharing = false;
        shareCamButton.innerHTML = 'ShareCamera';
        var rMessage = {
            userid: user.id,
            cameraSharing: false,
            microphoneSharing: false
        };
        that.socket.emit('share_cam', rMessage);
    }
    function stopSharingScreen() {
        if (screenStream) {
            screenStream.stop();
        }
        screenStream = null;
        isScreenSharing = false;
        shareScreenButton.innerHTML = 'ShareScreen';
        var rMessage = {
            userid: user.id,
            screenSharing: false
        };
        that.socket.emit('share_screen', rMessage);
    }

    //--------P2P--------
    // type => 1.cam, 2.mic, 3.cam & mic, 4.screen
    this.call = function(userid, type) {
        //console.log('call');
        var message = {
            offer: userid,
            answer: user.id,
            streamtype: type
        };

        var tmp = (type === 4) ? '-answer-screen' : '-answer-media';
        rtcPeerConnections[userid + tmp] = buildRtcPeerConnection(userid, type, false);

        that.socket.emit('call', message);
    }
    function getRTCPeerConnection(id, type, isOffer) {
        //console.log('getRTCPeerConnection, id is ' + id + ', type is ' + type + ', is_offer? ' + isOffer);
        var tmp1 = (isOffer === true) ? '-offer' : '-answer';
        var tmp2 = (type === 4) ? '-screen' : '-media';
        return rtcPeerConnections[id + tmp1 + tmp2];
    }
    function buildRtcPeerConnection(id, type, isOffer) {
        //console.log('buildRtcPeerConnection, id is ' + id + ', type is ' + type + ', is_offer? ' + isOffer);
        var rtcPeerConnection = new RTCPeerConnection(iceServers, optionalRtpDataChannels);
        rtcPeerConnection.onicecandidate = handleIceCandidate;
        rtcPeerConnection.onaddstream = handleRemoteStreamAdded;
        rtcPeerConnection.onremovestream = handleRemoteStreamRemoved;
        rtcPeerConnection.oniceconnectionstatechange = handleIceConnectionStateChange;
        rtcPeerConnection.onreadystatechange = handleReadyStateChange;

        // custom function
        rtcPeerConnection.onremotesdpset = onRemoteSDPSet;
        rtcPeerConnection.onoffercreated = onOfferCreated;
        rtcPeerConnection.isoffer = isOffer;

        function handleIceCandidate(event) {
            console.log('handleIceCandidate event');
            if (event.candidate) {
                var candidate = {
                    sdpMLineIndex: event.candidate.sdpMLineIndex,
                    candidate: event.candidate.candidate };
                var rMessage = {
                    from: user.id,
                    to: id,
                    candidate: candidate,
                    streamtype: type,
                    tag: rtcPeerConnection.isoffer
                };
                console.log('send candidate message to '+ rMessage.to);
                that.socket.emit('candidate', rMessage);
            } else {
                console.log('End of candidates.');
            }
        }
        function onOfferCreated(sdp) {
            //console.log('onOfferCreated');
            rtcPeerConnection.offerSDP = sdp;
            console.log('setLocalDescription');
            rtcPeerConnection.setLocalDescription(sdp, onOfferSDPSet, onError);
        }
        function onRemoteSDPSet() {
            //console.log('onRemoteSDPSet');
            rtcPeerConnection.createAnswer(onAnswerCreated, onError);
        }
        function onAnswerCreated(sdp) {
            //console.log('onAnswerCreated');
            rtcPeerConnection.answerSDP = sdp;
            console.log('setLocalDescription');
            rtcPeerConnection.setLocalDescription(sdp, onAnswerSDPSet, onError);
        }
        function onOfferSDPSet() {
            //console.log('onOfferSDPSet');
            var message = {
                offer: isOffer ? user.id : id,
                answer: isOffer ? id : user.id,
                sdp: rtcPeerConnection.offerSDP,
                streamtype: type
            };
            console.log('send offer message to ' + id);
            that.socket.emit('offer', message);
        }
        function onAnswerSDPSet() {
            var message = {
                offer: isOffer ? user.id : id,
                answer: isOffer ? id : user.id,
                sdp: rtcPeerConnection.answerSDP,
                streamtype: type
            };
            console.log('send answer message to ' + id);
            that.socket.emit('answer', message);
        }
        function handleRemoteStreamAdded(event) {
            //console.log('handleRemoteStreamAdded');
            if (type === 4) {
                remoteScreenStream = event.stream;
                attachMediaStream(remoteScr, remoteScreenStream);
            }
            else {
                remoteCameraStream = event.stream;
                attachMediaStream(remoteCam, remoteCameraStream);

                // TODO: Mix Audio from remote stream & local mic
                // TODO: Record video & audio to local disk, then upload to media-storage-server

                //var audioTracks = remoteCameraStream.getAudioTracks();

            }
        }
        function handleIceConnectionStateChange(event) {
            //console.log('handleIceConnectionStateChange');
            if (rtcPeerConnection.iceConnectionState === 'disconnected') {
                if (type === 4) {
                    if (screenStream) {
                        rtcPeerConnection.removeStream(screenStream);
                    }
                    if (remoteScreenStream) {
                        rtcPeerConnection.removeStream(remoteScreenStream);
                        remoteScreenStream.stop();
                        remoteScreenStream = null;
                    }
                }
                else if (type >= 1 && type <= 3) {
                    if (mediaStream) {
                        rtcPeerConnection.removeStream(mediaStream);
                    }
                    if (remoteCameraStream) {
                        rtcPeerConnection.removeStream(remoteCameraStream);
                        remoteCameraStream.stop();
                        remoteCameraStream = null;
                    }
                }
                //rtcPeerConnection.close();
            }
        }
        return rtcPeerConnection;
    }
    function handleRemoteStreamRemoved(event) {
        //console.log('handleRemoteStreamRemoved');

        // TODO: Stop recording
    }
    function handleReadyStateChange(event) {
        //console.log('handleReadyStateChange');
        //console.log(event);
    }
    function onError(error){
        console.log('onError', error);
    }

    //--------MESSAGE--------
    function sendMessage() {
        var text = messageInput.value;
        if ( text && text !== '') {
            var message = {
                text: text
            };
            that.socket.emit('text_message', message);
        }
    }
    function pressEnterToSendMessage(e) {
        if (e.keyCode == 13) {
            sendMessage();
        }
    }

    //--------DOM--------
    function refreshRoomListDOM(rooms) {
        var ul = document.getElementById('roomlist');
        ul.innerHTML = '';
        for (var i = 0; i < rooms.length; i++) {
            var li = document.createElement('li');
            //li.innerHTML = '<a href="/rooms/' + rooms[i].id + '">' + rooms[i].name + '</a>';
            li.innerHTML = '<a href="javascript:rtc.joinRoom(\'' + rooms[i].id + '\');">[' + (i+1) + '] ' + rooms[i].name + '</a>';
            ul.appendChild(li);
        }
    }
    function refreshRoomDOM(room) {
        if (room) {
            roomNameLabel.innerHTML = room.name;
            roomNameInput.setAttribute('readonly', 'readonly');
        }
        else {
            roomNameLabel.innerHTML = 'No room';
            roomNameInput.removeAttribute('readonly');
            refreshUserListDOM([]);
        }
    }
    function refreshUserListDOM(users) {
        var ul = document.getElementById('userlist');
        ul.innerHTML = '';
        for (var i = 0; i < users.length; i++) {
            var li = document.createElement('li');
            li.id = users[i].id + '-li';
            li.innerHTML = '<span>' + users[i].name + '</span>';
            if (users[i].id != user.id) {
                li.innerHTML += ' <a id="' + users[i].id + '-cam' + '" href="javascript:rtc.call(\''+ users[i].id +'\', 3);" class="button small"><i class="icon-camera-2 on-right"></i>Cam</a> ';
                li.innerHTML += ' <a id="' + users[i].id + '-scr' + '" href="javascript:rtc.call(\''+ users[i].id +'\', 4);" class="button small"><i class="icon-screen on-right"></i>Scr</a> ';
            }
            ul.appendChild(li);
            refreshUserDeviceDOM(users[i].id, users[i].name, users[i].cameraSharing, users[i].microphoneSharing, users[i].screenSharing);
        }
    }
    function refreshMessageListDOM(time, from, text, color) {
        var div = document.getElementById('messageList');
        var p = document.createElement('p');
        p.innerHTML = time + ' ' + from + ': ' + text;
        if (color) {
            p.style.backgroundColor = color;
        }
        div.appendChild(p);
        div.scrollTop = div.scrollHeight;
    }
    function refreshUserDeviceDOM(id, name, cam, mic, scr) {
        if (id == user.id) {
            return;
        }

        var camlink = document.getElementById(id + '-cam');
        var scrlink = document.getElementById(id + '-scr');
        if (cam == true) {
            camlink.setAttribute('class', 'button small');
            camlink.href = 'javascript:rtc.call("'+ id +'", 3);';
        }
        else if (cam == false) {
            camlink.setAttribute('class', 'bg-grey fg-white button small');
            camlink.href = 'javascript:void(0);';
        }
        else {
            // do nothing
        }
        if (scr == true) {
            scrlink.setAttribute('class', 'button small');
            scrlink.href = 'javascript:rtc.call("'+ id +'", 4);';
        }
        else if (scr == false) {
            scrlink.setAttribute('class', 'bg-grey fg-white button small');
            scrlink.href = 'javascript:void(0);';
        }
        else {
            // do nothing
        }
    }

    //--------Event Listeners--------
    var createRoomButton = document.getElementById('createRoomButton');
    var leaveRoomButton = document.getElementById('leaveRoomButton');
    var sendMessageButton = document.getElementById('sendMessageButton');
    var shareCamButton = document.getElementById('shareCamButton');
    var shareScreenButton = document.getElementById('shareScreenButton');
    var roomNameInput = document.getElementById('roomNameInput');
    var roomNameLabel = document.getElementById('roomNameLabel');
    var roomPasswordInput = document.getElementById('roomPasswordInput');
    var messageInput = document.getElementById('messageInput');
    var camWidthInput = document.getElementById('camWidthInput');
    var camHeightInput = document.getElementById('camHeightInput');
    var scrWidthInput = document.getElementById('scrWidthInput');
    var scrHeightInput = document.getElementById('scrHeightInput');
    var remoteCam = document.getElementById('remoteCam');
    var remoteScr = document.getElementById('remoteScr');
    var localCam = document.getElementById('localCam');
    var localScr = document.getElementById('localScr');

    createRoomButton.addEventListener('click', createRoom);
    leaveRoomButton.addEventListener('click', leaveRoom);
    sendMessageButton.addEventListener('click', sendMessage);
    shareCamButton.addEventListener('click', shareCam);
    shareScreenButton.addEventListener('click', shareScreen);

    messageInput.addEventListener('keydown', pressEnterToSendMessage);
    window.onbeforeunload = closingWindow;

    //return this;
}