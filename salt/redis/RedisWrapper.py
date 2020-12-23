import threading
import traceback
import redis


from redis.sentinel import Sentinel

from salt.selflog.manual_log import ManualLog

# Imports related to websocket

log = ManualLog().get_logger('salt_api_module')

class Singleton(object):
    _instance_lock = threading.Lock()

    def __init__(self, *args, **kwargs):
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(Singleton, "_instance"):
            with Singleton._instance_lock:
                if not hasattr(Singleton, "_instance"):
                    try:
                        Singleton._instance = object.__new__(cls)

                        Singleton._instance.master_pub_topic = kwargs.get('_master_pub_topic')
                        Singleton._instance.none_match_ip = 'no_ip_matched'
                        Singleton._instance.sub_node = kwargs.get('_sub_node')

                        redis_type = kwargs.get('_redis_type')

                        if not redis_type:
                            log.error(" can not find redis type !!!")
                        else:
                            if "cluster" == redis_type:
                                cluster_redis_host = kwargs.get('_cluster_redis_host')
                                cluster_redis_port = int(kwargs.get('_cluster_redis_port'))
                                cluster_redis_password = kwargs.get('_cluster_redis_password')

                                Singleton._instance._pool = redis.ConnectionPool(host= cluster_redis_host, port=cluster_redis_port, db=1, password=cluster_redis_password)
                                Singleton._instance.redisInstance = redis.StrictRedis(connection_pool=Singleton._instance._pool)

                                log.info(" Singleton cluster redis instance  is created  ....")
                            elif "sentinel" == redis_type:
                                redisIpConf = kwargs.get('_channel_redis_sentinel')
                                redisConfigure = []
                                redisIpSplit = redisIpConf.split(',')
                                for redisInfo in redisIpSplit:
                                    redisInfoSplit = redisInfo.split(':')
                                    redisConfigure.append((redisInfoSplit[0], redisInfoSplit[1]))

                                Singleton._instance.sentinel = Sentinel(redisConfigure)
                                Singleton._instance.redisInstance = Singleton._instance.sentinel.master_for('redis-master',
                                                                              password=kwargs.get('_channel_redis_password'))

                                #log.info("RedisWrapper self.sentinel.master_for......")
                                #log.info(" sentinel redis instance  is created  ....")
                            else:
                                log.error("unknown redis type : %s !!!" % redis_type )
                    except:
                        log.error(traceback.format_exc())
                        pass


        return Singleton._instance


if __name__ == '__main__':
    p = {"name": "worldcup"}
    s = Singleton(**p)
    print(s.name)
    s = Singleton()
    print(s.name)
    s = Singleton()
    print(s.name)