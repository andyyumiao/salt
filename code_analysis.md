
系统操作入口
==================

* salt主控命令: salt/scripts/salt.py
* salt apiv2: salt/scripts/salt-apiv2.py
* salt maid: salt/scripts/sal-maid.py
* salt ncp: salt/scripts/salt-ncp.py

salt主控命令（salt/scripts/salt.py）核心代码分析
==================
```
#读取redis配置
self.bootConfig = {'_sub_timeout': sub_timeout, '_sub_node': '',
                           '_channel_redis_sentinel': self.newopt.get('channel_redis_sentinel'),
                           '_channel_redis_password': self.newopt.get('channel_redis_password'),
                           '_master_pub_topic': self.newopt.get('id'),
                           '_redis_type': self.newopt.get('redis_type'),
                           '_cluster_redis_host': self.newopt.get('cluster_redis_host'),
                           '_cluster_redis_port': self.newopt.get('cluster_redis_port'),
                           '_cluster_redis_password': self.newopt.get('cluster_redis_password')
                           }

# 过滤ip列表，可以在/data0/md/ip.md文件中存储要排除的ip列表，salt执行时会自动从salt执行列表进行排除
def getPassedIp():
    import numpy
    numpy.warnings.filterwarnings('ignore')
    try:
        passed_ip = numpy.loadtxt('/data0/md/ip.md', dtype=numpy.str)
    except Exception:
        logger.info("====  ignore /data0/md/ip.md ======")
        return []
    return passed_ip.tolist()

#创建redis实例
clientPub = salt.newrun.MasterPub(**self.bootConfig)

#注册redis channel
redisChannel = clientPub.getRedisInstance().pubsub()

#订阅topic，用来监听salt maid执行返回结果
redisChannel.subscribe(wrapMesage['tempTopic'])
                
#将要执行的salt命令发送至redis通道
clientPub.publishToSyndicSub(salt.newrun.json.dumps(wrapMesage))

#开始消费salt maid返回数据
while True:
  #for message in redisChannel.listen():
      try:
          #获取返回消息
          message = redisChannel.get_message()
          ...
      except:
        logger.info(traceback.format_exc())
        pass
      #防止cpu空轮训
      time.sleep(0.001)

#取消本次命令订阅
redisChannel.unsubscribe(wrapMesage['tempTopic'])

#断开redis连接，本次命令执行结束
redisChannel.connection_pool.disconnect()

#如下是统计命令执行结果的汇总统计
for result in emptyRet:
    if result['ret_']:
        # begin print in client console
        self._output_ret(result['ret_'], result['out'])

for result in noResponseRet:
    if result['ret_']:
        for k, v in result['ret_'].items():
            if k not in sucset:
                # begin print in client console
                self._output_ret(result['ret_'], result['out'])

for result in noConnectRet:
    if result['ret_']:
        for k, v in result['ret_'].items():
            if k not in sucset:
                # begin print in client console
                self._output_ret(result['ret_'], result['out'])

disconnectedSyndic = set(comeSubList).difference(resultPingSet)
if disconnectedSyndic:
    print_cli('With disconnected syndic: %s' % list(disconnectedSyndic))

if len(timeoutSet) > 0 or len(lossSyndic) > 0:
    print('missed maids: {}\nmissed minions: {}'.format(",".join(lossSyndic), ",".join(timeoutSet)))

if len(repeatet) > 0:
    print('Find some minion run repeated: {}'.format(repeatet))

print('normal size: {}\nmissed size: {}\nempty size: {}'.format(normalsize, len(timeoutSet),
                                                                len(emptyRet)))
```

salt maid核心代码分析
==================
```
try:
    #获取maid节点对应minion id
    subNode = opts['id']
    from salt.newrun import (json, byteify, MessageType)
    
    #生成redis pubsub实例
    redischannel_sub = self.redisInstance.pubsub()
    
    #注册salt master id对应的topic
    redischannel_sub.subscribe(self._master_pub_topic.split(','))
    
    #开启redis监听，监听来自salt master下发的消息
    for message in redischannel_sub.listen():
        try:
            messageType = byteify(message)
            if messageType['type'] == 'message':
                maid_log.info("received master data: %s" % messageType['data'])

                wrapMesage = json.loads(messageType['data'])
                self.redisInstance.publish(wrapMesage['tempTopic'], json.dumps({'type': MessageType.PING, 'sub_ip': subNode}, ensure_ascii=False, encoding='utf-8'))

                ##fork sub process to handle the task
                maid_log.info("fork process for: %s" % wrapMesage)
                
                #开启进程，解析并处理salt master下发的命令
                p = multiprocessing.Process(target=self.run, args=(wrapMesage, subNode, opts))
                p.start()

        except Exception, e:
            maid_log.info(traceback.format_exc())
            #print('traceback.format_exc():\n%s' % traceback.format_exc())

except Exception, e:
    maid_log.info(traceback.format_exc())
```

salt apiv2核心代码分析
==================
```
#获取redis实例
redisWrapper = Singleton(**self.bootConfig)

#获取salt master id
selfIp = salt_config['id']

#生成redis pubsub实例
redisChannel = redisWrapper.redisInstance.pubsub()

#订阅redis回调topic
redisChannel.subscribe(wrapMesage['tempTopic'])

noResponseRet = []
noConnectRet = []
emptyRet = []
# retcodes = []

comeSubList = getAcceptIp()
if selfIp in comeSubList:
    comeSubList.remove(selfIp)

syndic_count = len(comeSubList)
resultCount = 0
pingCount = 0

resultPingSet = set()
resultExeSet = set()
executeStart = time.time()

# NOTE: must publish cmd after registered the redis listen
# else we will miss ping message
#发送salt命令到redis队列
redisWrapper.redisInstance.publish(redisWrapper.master_pub_topic, salt.newrun.json.dumps(wrapMesage))

#开启轮训监听
while True:
#for message in redisChannel.listen():
    try:
        #获取redis消息
        message = redisChannel.get_message()
        ...
    except:
      api_log.info(traceback.format_exc())
      pass
    #防止cpu空轮训
    time.sleep(0.001)
```

salt cp代码改造可参考上述逻辑
==================
