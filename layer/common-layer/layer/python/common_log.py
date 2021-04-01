#
#
# common_log出力共通Lambda
# 
# 
import os
import json
import common_util
import ast

LOG_DEBUG = 1
LOG_INFO = 2
LOG_WARNING = 3
LOG_ERROR = 4


if 'LOG_LEVEL' in os.environ:
    LOG_LEVEL = os.environ['LOG_LEVEL']
else:
    LOG_LEVEL = LOG_DEBUG

def output(loglevel, message, event = None, method = '', point = 0) -> None:
    '''
    LOG出力

    Parameters
    --------------------------------------------
    loglevel : int
        LOG_DEBUG < LOG_INFO < LOG_WARNING < LOG_ERROR 
    message : any
        出力メッセージ
    event : dict ( default = None)
        Lambda呼出し時の eventパラメータ
        ログ出力用の詳細情報を出力
    method : str ( default = '' )
        呼出し元関数名
    point : number (default = 0)
        呼出し元関数位置

    Returns
    --------------------------------------------
    None

    '''

    if loglevel < LOG_LEVEL:
        return

    if loglevel == LOG_DEBUG :
        level = 'D'
    elif loglevel == LOG_INFO :
        level = 'I'
    elif loglevel == LOG_WARNING :
        level = 'W'
    elif loglevel == LOG_ERROR :
        level = 'E'
    else:
        level = '?'

    params ={'resourceId':''
        ,'httpMethod':''
        ,'path':''
        ,'accountId':''
    }


    if event is not None :
        if 'requestContext' in event :
            for key in params.keys() :
                if key in event['requestContext']:
                    params[key] = event['requestContext'][key]
    
    print( 'Level:{0},resourceId:{1},path:{2}({3}),accountId:{4},{5},{6},{7}'.format(   \
        level, params['resourceId'], params['path'], params['httpMethod'],  \
        params['accountId'], message, method, point ))

if __name__ == '__main__':
    print('start')
    output(LOG_ERROR, 'メッセージ')

    msg_dict = {
                'KEY' : 'TEST'
                ,'DATA' : 3
                }
    output(LOG_ERROR, msg_dict)

    msg_list = ['bac', 123, 'aaaa']
    output(LOG_ERROR, msg_list)

    msg_tup = ('bac', 123, 'aaaa')
    output(LOG_ERROR, msg_tup)
 