
What is SaltStack?
==================

SaltStack makes software for complex systems management at scale.
SaltStack is the company that created and maintains the Salt Open
project and develops and sells SaltStack Enterprise software, services
and support. Easy enough to get running in minutes, scalable enough to
manage tens of thousands of servers, and fast enough to communicate with
them in *seconds*.

Salt is a new approach to infrastructure management built on a dynamic
communication bus. Salt can be used for data-driven orchestration,
remote execution for any infrastructure, configuration management for
any app stack, and much more.

Download Salt Open
==================

Salt Open is tested and packaged to run on CentOS, Debian, RHEL, Ubuntu,
Windows. Download Salt Open and get started now.

`<https://repo.saltstack.com/>`_

`Installation Instructions <https://docs.saltstack.com/en/latest/topics/installation/index.html>`_

SaltStack Documentation
=======================

Installation instructions, getting started guides, and in-depth API
documentation.

`<https://docs.saltstack.com/en/getstarted/>`_

`<https://docs.saltstack.com/en/latest/>`_

Get SaltStack Support and Help
==============================

**IRC Chat** - Join the vibrant, helpful and positive SaltStack chat room in
Freenode at #salt. There is no need to introduce yourself, or ask permission to
join in, just help and be helped! Make sure to wait for an answer, sometimes it
may take a few moments for someone to reply.

`<http://webchat.freenode.net/?channels=salt&uio=Mj10cnVlJjk9dHJ1ZSYxMD10cnVl83>`_

**Mailing List** - The SaltStack community users mailing list is hosted by
Google groups. Anyone can post to ask questions about SaltStack products and
anyone can help answer. Join the conversation!

`<https://groups.google.com/forum/#!forum/salt-users>`_

You may subscribe to the list without a Google account by emailing
salt-users+subscribe@googlegroups.com and you may post to the list by emailing
salt-users@googlegroups.com

**Reporting Issues** - To report an issue with Salt, please follow the
guidelines for filing bug reports:
`<https://docs.saltstack.com/en/develop/topics/development/reporting_bugs.html>`_

**SaltStack Support** - If you need dedicated, prioritized support, please
consider a SaltStack Support package that fits your needs:
`<http://www.saltstack.com/support>`_

Engage SaltStack
================

`SaltConf`_, **User Groups and Meetups** - SaltStack has a vibrant and `global
community`_ of customers, users, developers and enthusiasts. Connect with other
Salted folks in your area of the world, or join `SaltConf18`_, the SaltStack
annual user conference, September 10-14 in Salt Lake City. Please let us know if
you would like to start a user group or if we should add your existing
SaltStack user group to this list by emailing: info@saltstack.com

**SaltStack Training** - Get access to proprietary `SaltStack education
offerings`_ through instructor-led training offered on-site, virtually or at
SaltStack headquarters in Salt Lake City. SaltStack Enterprise training helps
increase the value and effectiveness of SaltStack software for any customer and
is a prerequisite for coveted `SaltStack Certified Engineer (SSCE)`_ status.
SaltStack training is also available through several `SaltStack professional
services`_ offerings.

**Follow SaltStack on -**

* YouTube - `<http://www.youtube.com/saltstack>`_
* Twitter - `<http://www.twitter.com/saltstack>`_
* Facebook - `<https://www.facebook.com/SaltStack/>`_
* LinkedIn - `<https://www.linkedin.com/company/salt-stack-inc>`_
* LinkedIn Group - `<https://www.linkedin.com/groups/4877160>`_
* Google+ - `<https://plus.google.com/b/112856352920437801867/+SaltStackInc/posts>`_

.. _SaltConf: http://www.youtube.com/user/saltstack
.. _global community: http://www.meetup.com/pro/saltstack/
.. _SaltConf18: http://saltconf.com/
.. _SaltStack education offerings: http://saltstack.com/training/
.. _SaltStack Certified Engineer (SSCE): http://saltstack.com/certification/
.. _SaltStack professional services: http://saltstack.com/services/

Developing Salt
===============

The Salt development team is welcoming, positive, and dedicated to
helping people get new code and fixes into SaltStack projects. Log into
GitHub and get started with one of the largest developer communities in
the world. The following links should get you started:

`<https://github.com/saltstack>`_

`<https://docs.saltstack.com/en/latest/topics/development/index.html>`_

`<https://docs.saltstack.com/en/develop/topics/development/pull_requests.html>`_


目录
==================
1.说明
2.源码安装
3.RPM打包
4.RPM安装
5.架构说明

说明
===============
由于重构了Salt Master和Salt Syndic之间的通信层，所以salt、salt-api、salt-job、salt-cp等均需作了适配改造。

* salt：基于redis pub/sub重构优化的salt主命令
* salt-maid：salt-syndic的替代品，运行在salts-syndic节点
* salt-apiv2：salt-api的替代品，运行在salt-master节点
* saltx：对应官方原生salt命令，运行在salt-master节点，用于控制salt-maid节点
* salt-minion：原生salt-minion。注意：在salt-maid节点上也需要启动该服务
* salt-ncp：对应原生salt-cp，只用来控制到salt-maid的文件传输
* salt-cp：已进行了重构，适配redis通信通道
* salt-syndic：已废弃。
* salt-api：已废弃。


源码安装
===============

* git clone https://github.com/andyyumiao/salt.git

* 1、进入/salt/录下，执行./setup.py install，会在/usr/bin/目录下生成salt-maid、saltx、salt-apiv2等启动脚本
* 2、修改salt master端配置文件，增加redis配置，vim /etc/salt/master
* 2.1、按redis哨兵集群方式配置：
```
redis_type: sentinel
channel_redis_sentinel: redis哨兵集群地址
channel_redis_password: redis密码
channel_sub_timeout: 30
#salt master ip
id: x.x.x.x
```

* 2.2、按redis cluster集群方式配置：
```
redis_type: cluster
cluster_redis_host: redis cluster集群地址
cluster_redis_port: 6379
cluster_redis_password: redis密码
channel_sub_timeout: 30
#salt master ip
id: x.x.x.x
```
* 3、修改salt maid端配置文件，增加redis配置，vim /etc/salt/master
* 3.1、按redis哨兵集群方式配置：
```
#salt master ip
super_master: x.x.x.x,x.x.x.x
channel_redis_sentinel: redis哨兵集群地址
channel_redis_password: redis密码
redis_type: sentinel
```

* 3.2、按redis cluster集群方式配置：
```
#salt master ip
super_master: x.x.x.x,x.x.x.x
redis_type: cluster
cluster_redis_host: redis cluster集群地址
cluster_redis_port: 6379
cluster_redis_password: redis密码
```
* 4、修依次登陆salt master、salt maid节点进行启动：salt-master -d、salt-maid -d


RPM打包（用于RPM方式安装，目前尚不可靠，不建议使用，待优化）
===============

* 安装rpm：yum install rpmdevtools && yum install -y rpm-build && rpmdev-setuptree
* 创建rpm工作区目录：
    ~/rpmbuild/BUILD  ~/rpmbuild/BUILDROOT  ~/rpmbuild/RPMS  ~/rpmbuild/SOURCES  ~/rpmbuild/SPECS  ~/rpmbuild/SRPMS
* 修改/salt/pkg/rpm下salt.spec文件：Version以及%global srcver字段修改为新版本号
* 修改/salt/_version.py中版本号，与salt.spec一致
* 将/salt打包为salt-x.x.x.tar.gz，将salt-x.x.x.tar.gz放入/root/rpmbuild/SOURCES/
* 将/salt/pkg/rpm/下所有文件放入/root/rpmbuild/SOURCES/
* 进入/salt/pkg/rpm/，执行rpmbuild -bb salt.spec
* 构建好的rpm包在/root/rpmbuild/RPMS/noarch/下

RPM安装
===============
* 说明：使用yum本地安装模式
* 步骤：将RPM包放入任意目录下，执行：yum localinstall salt-x.x.x-1.el7.centos.noarch.rpm salt-master-x.x.x-1.el7.centos.noarch.rpm salt-minion-x.x.x-1.el7.centos.noarch.rpm salt-syndic-x.x.x-1.el7.centos.noarch.rpm salt-maid-x.x.x-1.el7.centos.noarch.rpm

架构说明
===============

* 重构架构图
<p align="center">
<img src="https://camo.githubusercontent.com/04bf964a33378a1424ddf5b1696f81f9f2cc9e4d69368ae04f02d14e45edab58/687474703a2f2f73746f726167652e6a642e636f6d2f6264702d75706c6f616465642d66696c65732f3230313930343034313033312d32396639646235612d346435642d346333622d626666372d3063343134633462393433646d61782e706e673f457870697265733d33373031383238373138264163636573734b65793d36663465393435613164353536653664383764396266343163376364666333663131646132646332265369676e61747572653d4457556845657656616f6f71586a314d78306147515969642532423538253344" alt="SaltStrcut" title="SaltStrcut" />
</p>


* 重构启动流程
<p align="center">
<img src="https://camo.githubusercontent.com/a16383c452c33bbe27313c0cd6513c25e6c25dfde8f1d45caca8d534426861ce/687474703a2f2f73746f726167652e6a642e636f6d2f6264702d75706c6f616465642d66696c65732f3230313930343034313033332d31626234613162622d353932312d343436652d616431302d6364346134363236396536646d61782e706e673f457870697265733d33373031383238383539264163636573734b65793d36663465393435613164353536653664383764396266343163376364666333663131646132646332265369676e61747572653d54496c6866565a4c6955793868594f427435765857363078556b77253344" alt="SaltBoot" title="SaltBoot" />
</p>
