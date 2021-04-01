#--------------------------------------------------------------
# history.py
# 業務経歴書処理
#
# 
#
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
import common_util
from typing import Tuple


def init(event) -> Tuple[dict, dict]:
    '''
    初期処理

    Parameters
    ----------------------------------------------
    event : dict
        Lambda実行時パラメータ

    Returns
    ----------------------------------------------
    param_dict 
        パラメータから取得した情報を格納
    param_record
        DBに登録する情報(パラメータ['body']の情報 + ユーザID)
    '''

    #環境情報取得
    param_dict = common_util.get_env()
    # パラメータ取得
    if 'origin' in event['headers']:
        param_dict[common_const.ENV_ACCESS_CONTROL_ALLOW_ORIGIN] = event['headers']['origin']
    # ユーザID取得
    param_dict[common_const.PARAM_USERID] = event['pathParameters'][common_const.PARAM_USERID]
    print(param_dict[common_const.PARAM_USERID])
    # ENV_ACCESS_CONTROL_ALLOW_ORIGINの値をevent['headers']['origin']が設定されていた場合は
    # 入替て設定する
    if 'origin' in event['headers']:
        print('set headers origin')
        param_dict[common_const.ENV_ACCESS_CONTROL_ALLOW_ORIGIN] = event['headers']['origin']    
    
    # 登録する業務案件データ、キー情報のユーザIDをDICTへ設定
    #param_record = json.loads(event['body'],'utf-8')
    param_record = json.loads(event['body'])
    param_record[common_const.PARAM_USERID]=param_dict[common_const.PARAM_USERID]

    return param_dict, param_record


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

def main(param_dict, param_record, ret_dict ) -> dict :
    '''
    メイン関数

    Parameters
    ----------------------------------------------
    param_dict : dict
        初期情報格納dict
    param_record : dict
        登録用パラメータ
    ret_dict : dict
        返却用のdict
    Returns
    ----------------------------------------------
    '''
    try:
        if param_dict[common_const.DYNAMODB_ENDPOINT]:
            print('endpoint url={0} '.format(param_dict[common_const.DYNAMODB_ENDPOINT]))
            dynamodb = boto3.resource('dynamodb', endpoint_url=param_dict[common_const.DYNAMODB_ENDPOINT])
        else:
            print('endpoint url=Nothing')
            dynamodb = boto3.resource('dynamodb')
        #
        # 登録処理
        table_t_work_history = dynamodb.Table(param_dict[common_const.ENV_T_WORK_HISTORY])
        response = table_t_work_history.put_item(Item = param_record)
        common_log.output(common_log.LOG_INFO, response, None,'main',1002)
        ret_dict['body'] = json.dumps(param_record)
        ret_dict['statusCode'] = common_const.SUCCESS_CODE
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

def post(event, context) :
    '''
    POST開始関数

    業務経歴の新規登録処理

    Parameters
    ----------------------------------------------
    event : dict
    context : dict

    Returns
    ----------------------------------------------

    '''
    try :
        common_log.output(
            common_log.LOG_INFO
            ,'START'
            ,event
            ,'post'
            ,100
        )
        #初期処理
        param_dict, param_record = init(event)
        common_log.output(common_log.LOG_DEBUG, param_dict,event,'post',101)
        common_log.output(common_log.LOG_DEBUG, param_record,event,'post',102)

        # 返却ヘッダ設定
        ret_dict = get_response(param_dict)
        # メイン処理実行
        ret_dict = main(param_dict, param_record, ret_dict)
        common_log.output(common_log.LOG_DEBUG, param_record,event,'post',103)
        return ret_dict
    except :
        traceback.print_exc()
        print('例外発生')
        return

