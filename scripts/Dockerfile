FROM docker.io/fedora
MAINTAINER ggxx120<ggxx120@gmail.com>

RUN yum -y update;\
    yum -y install passwd openssh-server nodejs npm make emacs nano vim git wget gcc gcc-c++ gdb autoconf automake net-tools tar gzip bzip2 qemu tigervnc-server;\
    yum -y install @lxde-desktop;\
    yum -y install firefox;\
    npm install -g tty.js;\
    yum clean all
RUN cd /opt && git clone git://github.com/kanaka/noVNC
RUN	mkdir /root/.ssh;\
    mkdir /opt/ttyjs;\
    mkdir /root/.vnc

CMD ["/usr/sbin/sshd", "-D"]

ENTRYPOINT ["/usr/bin/bash"]