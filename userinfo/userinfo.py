#--------------------------------------------------------------
# userinfo
# ユーザアカウント情報取得
#
# url:/userinfo/{userid}
# method:get
#
#--------------------------------------------------------------
import os
import json
import boto3
import traceback
from decimal import Decimal
from boto3.dynamodb.conditions import Key
import common_log
import common_const

'''
ENV_ACCESS_CONTROL_ALLOW_ORIGIN = 'ACCESS_CONTROL_ALLOW_ORIGIN'
ENV_M_USER = 'TABLE_M_USER'
PARAM_USERID = 'uuid'
ERROR_MESSAGE = 'サーバエラーが発生しました'
DYNAMODB_ENDPOINT='DYNAMODB_ENDPOINT'
SUCCESS_CODE = 200
ERROR_REQUEST = 400
ERROR_INTERNAL = 500
'''

def decimal_default_proc(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def get_env() -> dict:
    '''
    環境情報取得

    Parameters
    ----------------------------------------------

    Returns
    ----------------------------------------------
    環境情報 : dict

    '''
    param_dict = {}
    param_dict[common_const.ENV_ACCESS_CONTROL_ALLOW_ORIGIN] = os.environ[common_const.ENV_ACCESS_CONTROL_ALLOW_ORIGIN]
    param_dict[common_const.ENV_M_USER] = os.environ[common_const.ENV_M_USER]
    param_dict[common_const.DYNAMODB_ENDPOINT] = os.environ[common_const.DYNAMODB_ENDPOINT]
    return param_dict

def init(event) -> dict:
    '''
    初期処理

    Parameters
    ----------------------------------------------
    event : dict
        Lambda実行時パラメータ

    Returns
    ----------------------------------------------

    '''
    param_dict = get_env()
    # パラメータ取得
    param_dict[common_const.PARAM_USERID] = event['pathParameters'][common_const.PARAM_USERID]

    if 'origin' in event['headers']:
        param_dict[common_const.ENV_ACCESS_CONTROL_ALLOW_ORIGIN] = event['headers']['origin']
        
    return param_dict

def get_response(param_dict) -> dict :
    return {
        'headers': {
            #'Content-Type': 'application/json'
            # CORS設定 '*' だけで動いたけどとりあえず設定しておく
            #
            # 'Access-Control-Allow-Origin': '*'  
            #,'Vary':'Origin'
            'Access-Control-Allow-Origin': param_dict[common_const.ENV_ACCESS_CONTROL_ALLOW_ORIGIN]
            ,'Access-Control-Allow-Methods':'GET, PUT, DELETE, OPTIONS'
            ,'Access-Control-Allow-Headers':'X-Requested-With, X-HTTP-Method-Override, Content-Type, Accept'
            ,'Access-Control-Allow-Credentials':'true'
        }
        ,'isBase64Encoded': False
    }        

def main(param_dict, ret_dict) -> dict :
    '''
    メイン関数

    Parameters
    ----------------------------------------------
    param_dict : dict
        初期情報格納dict
    ret_dict : dict
        返却用のdict
    Returns
    ----------------------------------------------
    '''
    try:
        print('主処理')

        if param_dict[common_const.DYNAMODB_ENDPOINT]:
            print('endpoint url={0} '.format(param_dict[common_const.DYNAMODB_ENDPOINT]))
            dynamodb = boto3.resource('dynamodb', endpoint_url=param_dict[common_const.DYNAMODB_ENDPOINT])
        else:
            print('endpoint url=Nothing')
            dynamodb = boto3.resource('dynamodb')
        table_m_user = dynamodb.Table(param_dict[common_const.ENV_M_USER])
        response = table_m_user.query(
            KeyConditionExpression=Key('uuid').eq(param_dict[common_const.PARAM_USERID])
        )
        print('get_item')
        print(response)
        user_dict = response['Items'][0];
        #ret_dict['body'] = json.dumps(user_dict)
        ret_dict['body'] = json.dumps(user_dict, default=decimal_default_proc)

        ret_dict['statusCode'] = common_const.SUCCESS_CODE
        #print('result dict')
        #print(ret_dict)
        return ret_dict
    except:
        print('メイン処理で例外発生')
        traceback.print_exc()
        errmsg = {
            'message': common_const.ERROR_MESSAGE_001
        }
        ret_dict['body'] = json.dumps(errmsg)
        ret_dict['statusCode'] = common_const.ERROR_REQUEST
        return ret_dict    

def run(event,context):
    '''
    開始関数

    Parameters
    ----------------------------------------------
    event : dict
    context : dict

    Returns
    ----------------------------------------------

    '''

    # 初期処理で例外が発生した場合はクライアントへメッセージが返却出来ないため
    # ログ出力後終了する。
    try :
        print('start')
        common_log.output(
            common_log.LOG_INFO
            ,'START'
            ,event
            ,'run'
            ,1
        )

        print(event)
        #初期処理
        print('初期処理')
        param_dict = init(event)
        print('パラメータ情報')
        print(param_dict)    

        # 返却ヘッダ設定
        ret_dict = get_response(param_dict)
        # メイン処理実行
        ret_dict = main(param_dict, ret_dict)
        print(ret_dict)
        return ret_dict
    except :
        print('初期処理で例外発生')
        traceback.print_exc()
        return

if __name__ == '__main__':
    print('start')
    common_log.output(common_log.LOG_ERROR, 'メッセージ')
