var crypto = require('crypto');
var process = require('child_process');
var colors = require('colors');
var fs = require('fs');

function _sha1(str) {
    var md5sum = crypto.createHash('sha1');
    md5sum.update(str, 'utf8');
    return md5sum.digest('hex');
}

function _isEmpty(obj) {
    for (var name in obj) {
        return false;
    }
    return true;
};

function s4() {
	return Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);
}

function _createShortId() {
	return s4();
}

function _createLongId() {
	return s4() + s4() + s4() + s4() + s4() + s4() + s4() + s4();
	//return s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4();
}

function _getTime() {
	var date = new Date();
	return date.toLocaleTimeString();
	//return date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();
}


exports.sha1 = _sha1;
exports.isEmpty = _isEmpty;
exports.createLongId = _createLongId;
exports.createShortId = _createShortId;
exports.getTime = _getTime;
