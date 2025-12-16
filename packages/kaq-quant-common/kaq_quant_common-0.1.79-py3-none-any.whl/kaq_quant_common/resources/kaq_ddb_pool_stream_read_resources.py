import os
import dolphindb as ddb
import dolphindb.settings as keys
from dolphindb.settings import SqlStd
from kaq_quant_common.utils import yml_utils
import pandas as pd
import threading
from kaq_quant_common.utils.logger_utils import get_logger
import traceback

mutex = threading.Lock()

class KaqQuantDdbPoolStreamReadRepository:
    '''
    连接池方式连接DolphinDB数据库, 支持流数据表读取
    '''
    def __init__(self, host, port, user, passwd, pool_size=1):
        self.logger = get_logger(self)
        try:
            mutex.acquire()
            
            # 连接地址为localhost，端口为8848的DolphinDB，登录用户名为admin，密码为123456的账户，连接数为8
            self.pool = ddb.DBConnectionPool(host, port, pool_size, user, passwd, 
                                             loadBalance=True, 
                                             compress=True, 
                                             protocol=keys.PROTOCOL_DDB,
                                             reConnect=True, 
                                            #  tryReconnectNums=5, # 若不开启高可用，须与 reconnect 参数搭配使用，对单节点进行有限次重连。若不填写该参数，默认进行无限重连。
                                             sqlStd=SqlStd.DolphinDB,
                                             )
        except Exception as e:
            self.logger.error(f'KaqQuantDdbPoolStreamReadRepository.__init__ is occured error: {str(e)} - {str(traceback.format_exc())}')
        finally:
            mutex.release()

    async def query(self, query: str, colums:list=None) -> pd.DataFrame:
        '''
        从流数据表中获取数据
        '''
        try:
            data = await self.pool.run(query, pickleTableToList=True, clearMemory=True)
            if data is None:
                return pd.DataFrame(), None
            big_df = pd.DataFrame(data).T
            if colums is None:
                return big_df, None
            if len(colums) != len(big_df.columns):
                return big_df, 'Nonequal length'
            big_df.columns = colums
            return big_df, None
        except Exception as e:
            self.logger.error(f'KaqQuantDdbPoolStreamReadRepository.getStreamQuery is occured error: {str(e)} - {str(traceback.format_exc())}')
        return pd.DataFrame()


if __name__ == '__main__':
    host, port, user, passwd = yml_utils.get_ddb_info(os.getcwd())
    kaq = KaqQuantDdbPoolStreamReadRepository(host, port, user, passwd)
    df = kaq.query(f"select count(*) from kaq_all_future_limit_order_streaming")
    print(df.head(5))