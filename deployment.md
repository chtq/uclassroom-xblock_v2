How to Deployment
========

### GitLab Server
* Enable sign up
Edit file ```<gitlab_path>/config/gitlab.yml```, set:```sigup_enabled: true```
* Disable email confirmation  
  Edit file ```<gitlab_path>/app/model/user.rb```, comment ```confirmable ``` after ```devise``` section  
  Edit file ```<gitlab_path>/app/views/devise/session/new.html.haml```, comment the HTML tag which contains ```new_confirmation_path(resource_name)```
* Create teacher account and build labs' projects. Make sure projects are public
* Reboot

### Docker Server
* Create your own TLS keys with OpenSSL if you don't have any  
  Here are some useful links  
  http://docs.docker.com/articles/https/  
  http://longgeek.com/2014/09/14/docker-using-https/  
* Then you will get at least five pem files: ```ca.pem```, ```server-cert.pem```, ```server-key.pem```, ```cert.pem``` and ```key.pem```  
* To start docker daemon, use:  
```
$sudo docker -d --tlscacert=<ca.pem> --tlscert=<server-cert.pem> --tlskey=<server-key.pem> -H=0.0.0.0:2376
```

### Node.js Server
* To install ```node.js``` and ```npm```, use:  
```
$sudo yum install nodejs, npm
```  
, or  
```
$sudo apt-get install nodejs, npm
```  
* In rtc_node folder, use: ```$npm install``` to install node modules
* Edit file ```config.json```, its default parameters are:  
```
{
"PORT"            : 1986,
"MAX_USER_NUM_OF_ROOM": 2
}
```
* Use ```$node app.js``` to start node.js server listening

### OpenEDX Server
* To install docker, please visit http://docs.docker.com/installation/ubuntulinux/#ubuntu-precise-1204-lts-64-bit
* Set environment variable  
```
DOCKER_HOST=tcp://docker_server_domain:2376
```  

### uc_rtc XBlock
* Edit file ```uc_rtc/uc_rtc/static/js/src/static.js```, set SOCKET_IO_URL:  
```
var SOCKET_IO_URL = 'http://<node.server.host>:<port>';
```
* To install uc_rtc XBlock on open-edx server, , use:  
```
$sudo -u edxapp /edx/bin/pip.edxapp install <path_of_uc_rtc>
```
* To restart edxapp service, use:  
```
$sudo /edx/bin/supervisorctl -c /edx/etc/supervisord.conf restart edxapp:
```

### uc_docker XBlock
* Edit file ```uc_docker/uc_docker/config.py```, set your own configuration
* To install uc_docker XBlock on open-edx server, use:  
```
$sudo -u edxapp /edx/bin/pip.edxapp install <path_of_uc_docker>
```
* To restart edxapp service, use:  
```
$sudo /edx/bin/supervisorctl -c /edx/etc/supervisord.conf restart edxapp:
```

### Memos
* All ```<var>``` are up to your own environment
* You can edit ```/etc/hosts```, if you don't have domain name, and be careful to make sure your TLS keys are valid.
* To uninstall uc_rtc or uc_docker, use:  
```
$sudo -u edxapp /edx/bin/pip.edxapp uninstall uc-rtc-xblock
```  
  , or  
```
$sudo -u edxapp /edx/bin/pip.edxapp uninstall uc-docker-xblock
```
