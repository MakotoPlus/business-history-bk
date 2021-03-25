#
#
# common_log出力共通Lambda
# 
# 
import os

LOG_DEBUG = 1
LOG_INFO = 2
LOG_ERROR = 3
LOG_LEVEL = LOG_DEBUG

if 'LOG_LEVEL' in os.environ:
    LOG_LEVEL = os.environ['LOG_LEVEL']

def output(loglevel, message, event = None, method = '', point = 0) -> dict:

    if loglevel < LOG_LEVEL:
        return

    if loglevel == LOG_DEBUG :
        level = 'D'
    elif loglevel == LOG_INFO :
        level = 'I'
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