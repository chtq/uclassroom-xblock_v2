部署
========

### GitLab 服务器
* 允许用户注册后不需要验证邮件即可登录  


### Docker 服务器
* 安装docker
* 创建密钥
  编辑脚本`scripts/pemgen.sh`，设置环境变量`UC_DOMAIN`为Docker服务器的域名  
  执行脚本`scripts/pemgen.sh`，然后将会在`scripts/certs`文件夹下看到生成的若干密钥
* 使用以下命令，启动Docker服务：  
```
$sudo docker -d --tlsverify --tlscacert=<ca.pem> --tlscert=<server-cert.pem> --tlskey=<server-key.pem> -H=0.0.0.0:2376
```
* 访问Docker服务器，添加默认镜像，在`scripts`目录下找到Dockerfile文件，执行： 
```
$sudo docker --tlsverify -H=<docker-server>:<port> --tlscacert=<ca.pem> --tlscert=<cert.pem> --tlskey=<key.pem> pull docker.io/fedora
```
```
$sudo docker --tlsverify -H=<docker-server>:<port> --tlscacert=<ca.pem> --tlscert=<cert.pem> --tlskey=<key.pem> build --rm -t uclassroom/ucore-vnc-base .
```


### Node.js 服务器
* 安装 `node.js` 和 `npm`：  
```
$sudo yum install nodejs, npm
```  
  ，或者  
```
$sudo apt-get install nodejs, npm
```  
* 进入 `rtc_node` 文件夹下， 执行以下命令，安装子模块：  
```
$npm install
```  
* 编辑文件 `config.json`， 其默认参数为：  
```
{
"PORT": 1986,
"MAX_USER_NUM_OF_ROOM": 2
}
```
* 使用 `$node app.js` 启动Node.js监听服务


### Open edX 服务器
* 在Open edX服务器上安装docker，请参考[这里](http://docs.docker.com/installation/ubuntulinux/#ubuntu-precise-1204-lts-64-bit)  


### uc_rtc XBlock
* 编辑文件 `uc_rtc/uc_rtc/static/js/src/static.js`， 设置全局变量 `SOCKET_IO_URL`：  
```
var SOCKET_IO_URL = 'http://<node.server.host>:<port>';
```
* 执行以下命令安装 uc_rtc XBlock：  
```
$sudo -u edxapp /edx/bin/pip.edxapp install <path_of_uc_rtc>
```
* 重启edxapp服务:  
```
$sudo /edx/bin/supervisorctl -c /edx/etc/supervisord.conf restart edxapp:
```


### uc_docker XBlock
* 编辑文件 `uc_docker/uc_docker/config.py`, 配置参数
* 执行以下命令安装 uc_docker XBlock：  
```
$sudo -u edxapp /edx/bin/pip.edxapp install <path_of_uc_docker>
```
* 重启edxapp服务:  
```
$sudo /edx/bin/supervisorctl -c /edx/etc/supervisord.conf restart edxapp:
```

### 备注
* 所有的 `<var>` 取决于你自己的服务器环境
* 卸载 uc_rtc 和 uc_docker的命令是：  
```
$sudo -u edxapp /edx/bin/pip.edxapp uninstall uc-rtc-xblock
```  
  ，和
```
$sudo -u edxapp /edx/bin/pip.edxapp uninstall uc-docker-xblock
```
