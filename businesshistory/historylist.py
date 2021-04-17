#--------------------------------------------------------------
# historylist.py
# 業務経歴書リスト処理
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
        DBに検索する情報
    '''

    #環境情報取得
    param_dict = common_util.get_env()
    # パラメータ取得
    if 'origin' in event['headers']:
        param_dict[common_const.ENV_ACCESS_CONTROL_ALLOW_ORIGIN] = event['headers']['origin']
    # ユーザID取得
    #param_dict[common_const.PARAM_USERID] = event['pathParameters'][common_const.PARAM_USERID]
    param_record = {}
    param_record[common_const.PARAM_USERID]=event['pathParameters'][common_const.PARAM_USERID]
    param_record[common_const.PARAM_PAGE_INDEX]=event['pathParameters'][common_const.PARAM_PAGE_INDEX]

    print(param_record)
    # ENV_ACCESS_CONTROL_ALLOW_ORIGINの値をevent['headers']['origin']が設定されていた場合は
    # 入替て設定する
    if 'origin' in event['headers']:
        print('set headers origin')
        param_dict[common_const.ENV_ACCESS_CONTROL_ALLOW_ORIGIN] = event['headers']['origin']    
    
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
        common_log.output(common_log.LOG_DEBUG,param_record, None,'main', 301)
        table_t_work_history = dynamodb.Table(param_dict[common_const.ENV_T_WORK_HISTORY])
        responses = table_t_work_history.query(
            KeyConditionExpression=Key('uuid').eq(param_record[common_const.PARAM_USERID])
            ,ScanIndexForward = False)
        common_log.output(common_log.LOG_DEBUG,responses, None,'main', 302)

        # 返却データは、最大表示件数分のみを抽出して返す
        start_index = int(param_record[common_const.PARAM_PAGE_INDEX]) * common_const.PARAM_PAGE_MAX
        max_index = start_index + common_const.PARAM_PAGE_MAX
        #max_index = start_index + 2
        #res = list(filter(lambda x: ( x >= start_index and x <= max_index), responses['Items']))
        res = responses['Items'][start_index:max_index]
        ret_dict['body'] = json.dumps(res, default=common_util.jsondumps_custom_proc)
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

def get(event, context) :
    '''
    GET開始関数

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
            ,'get'
            ,100
        )
        common_log.output(
            common_log.LOG_DEBUG
            ,event
            ,event
            ,'get'
            ,101
        )
        #初期処理
        param_dict, param_record = init(event)
        common_log.output(common_log.LOG_DEBUG, param_dict,event,'get',102)
        common_log.output(common_log.LOG_DEBUG, param_record,event,'get',103)
        # 返却ヘッダ設定
        ret_dict = get_response(param_dict)
        # メイン処理実行
        ret_dict = main(param_dict, param_record, ret_dict)
        common_log.output(common_log.LOG_DEBUG, ret_dict,event,'get',104)
        return ret_dict
    except :
        traceback.print_exc()
        print('例外発生')
        return
