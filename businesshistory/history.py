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
from datetime import datetime
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
    

    http_method = event['httpMethod'] if 'httpMethod' in event else ''


    # 登録する業務案件データ、キー情報のユーザIDをDICTへ設定
    param_record = {}
    if http_method == 'POST' or http_method == 'PUT':
        if 'body' in event :
            # Delete などは body が none
            #if None != event['body'] :
            param_record = json.loads(event['body'])


    #param_record = json.loads(event['body'],'utf-8')
    param_record[common_const.PARAM_USERID]=param_dict[common_const.PARAM_USERID]

    #
    # RENGE KEY取得
    if http_method == 'POST' :
        # 登録時はRANGEKEYを生成
        param_record[common_const.PARAM_RANGEKEY] = \
            (param_record['work_from'] + '-' + datetime.now().strftime('%Y%m%d%H%M%S')).replace('/','-');
    elif http_method == 'DELETE' :
        # DELETE
        param_record[common_const.PARAM_RANGEKEY] = event['pathParameters'][common_const.PARAM_RANGEKEY]
    elif http_method == 'PUT' :
        param_dict[common_const.PARAM_RANGEKEY] = event['pathParameters'][common_const.PARAM_RANGEKEY]
        param_record[common_const.PARAM_RANGEKEY] = \
            (param_record['work_from'] + '-' + datetime.now().strftime('%Y%m%d%H%M%S')).replace('/','-');
    
    # 更新日付を設定
    param_record[common_const.ENV_COLUMN_UPDATE_DATE] = common_util.get_datetime();    

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

def post_main(param_dict, param_record, ret_dict ) -> dict :
    '''
    POSTメイン関数

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
        method_name = 'post_main'
        #if param_dict[common_const.DYNAMODB_ENDPOINT]:
        #    print('endpoint url={0} '.format(param_dict[common_const.DYNAMODB_ENDPOINT]))
        #    dynamodb = boto3.resource('dynamodb', endpoint_url=param_dict[common_const.DYNAMODB_ENDPOINT])
        #else:
        #    print('endpoint url=Nothing')
        #    dynamodb = boto3.resource('dynamodb')
        #
        #
        #table_t_work_history = dynamodb.Table(param_dict[common_const.ENV_T_WORK_HISTORY])

        # 登録処理
        table_t_work_history = get_t_workhistory_table(param_dict)
        # 登録日付を設定
        param_record[common_const.ENV_COLUMN_INSERT_DATE] = param_record[common_const.ENV_COLUMN_UPDATE_DATE];
        common_log.output(
            common_log.LOG_DEBUG
            ,param_record
            ,None
            ,method_name
            ,301
        )
        response = table_t_work_history.put_item(Item = param_record)
        common_log.output(common_log.LOG_INFO, response, None, method_name,302)
        ret_dict['body'] = json.dumps(param_record)
        ret_dict['statusCode'] = common_const.SUCCESS_CODE
        return ret_dict
    except:
        print('POSTメイン処理で例外発生')
        traceback.print_exc()
        errmsg = {
            'message': common_const.ERROR_MESSAGE_001
        }
        ret_dict['body'] = json.dumps(errmsg)
        ret_dict['statusCode'] = common_const.ERROR_REQUEST
        return ret_dict    

def put_main(param_dict, param_record, ret_dict ) -> dict :
    '''
    PUTメイン関数

    FROM_TOがRANGEキーとなっている。更新される場合があるため、
    処理的にはDELETE & INSERT となる。

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
        method_name = 'put_main'

        common_log.output(common_log.LOG_DEBUG, param_record
            ,None ,method_name, 501)
        table_t_work_history = get_t_workhistory_table(param_dict)
        #
        # 削除時のキー情報はparam_dict内のパラメータから行う
        # param_recordには登録用の値が設定されている
        response = table_t_work_history.delete_item(
            Key ={
                'uuid' : param_record[common_const.PARAM_USERID]
                ,'rangekey' : param_dict[common_const.PARAM_RANGEKEY]
            }
        )
        common_log.output(common_log.LOG_DEBUG, response
            ,None ,method_name, 502)

        # 登録処理
        common_log.output(common_log.LOG_DEBUG, param_record
            ,None ,method_name, 503)
        response = table_t_work_history.put_item(Item = param_record)
        common_log.output(common_log.LOG_INFO, response, None, method_name,504)
        ret_dict['body'] = json.dumps(param_record)
        ret_dict['statusCode'] = common_const.SUCCESS_CODE
        return ret_dict
    except:
        print('POSTメイン処理で例外発生')
        traceback.print_exc()
        errmsg = {
            'message': common_const.ERROR_MESSAGE_001
        }
        ret_dict['body'] = json.dumps(errmsg)
        ret_dict['statusCode'] = common_const.ERROR_REQUEST
        return ret_dict    



def get_t_workhistory_table(param_dict):
    '''
    パラメータ内容からT_WORK_HISTORY_TABLEのリソースを返す
    '''
    if param_dict[common_const.DYNAMODB_ENDPOINT]:
        print('endpoint url={0} '.format(param_dict[common_const.DYNAMODB_ENDPOINT]))
        dynamodb = boto3.resource('dynamodb', endpoint_url=param_dict[common_const.DYNAMODB_ENDPOINT])
    else:
        print('endpoint url=Nothing')
        dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table(param_dict[common_const.ENV_T_WORK_HISTORY])


def delete_main(param_dict, param_record, ret_dict ) -> dict :
    '''
    DELETEメイン関数

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
        method_name = 'delete_main'
        
        #if param_dict[common_const.DYNAMODB_ENDPOINT]:
        #    print('endpoint url={0} '.format(param_dict[common_const.DYNAMODB_ENDPOINT]))
        #    dynamodb = boto3.resource('dynamodb', endpoint_url=param_dict[common_const.DYNAMODB_ENDPOINT])
        #else:
        #    print('endpoint url=Nothing')
        #    dynamodb = boto3.resource('dynamodb')
        #
        # 登録処理
        #table_t_work_history = dynamodb.Table(param_dict[common_const.ENV_T_WORK_HISTORY])

        table_t_work_history = get_t_workhistory_table(param_dict)
        common_log.output(
            common_log.LOG_DEBUG
            ,param_record
            ,None
            ,method_name
            ,401
        )
        response = table_t_work_history.delete_item(
            Key ={
                'uuid' : param_record[common_const.PARAM_USERID]
                ,'rangekey' : param_record[common_const.PARAM_RANGEKEY]
            }
        )
        common_log.output(common_log.LOG_INFO, response, None, method_name,402)
        #ret_dict['body'] = json.dumps(param_record)
        ret_dict['body'] = json.dumps('Delete Success')
        ret_dict['statusCode'] = common_const.SUCCESS_CODE
        return ret_dict
    except:
        print('DELETEメイン処理で例外発生')
        traceback.print_exc()
        errmsg = {
            'message': common_const.ERROR_MESSAGE_001
        }
        ret_dict['body'] = json.dumps(errmsg)
        ret_dict['statusCode'] = common_const.ERROR_REQUEST
        return ret_dict    
    
def run(event, context) :
    '''
    処理開始関数

    業務経歴の新規登録処理

    Parameters
    ----------------------------------------------
    event : dict
    context : dict

    Returns
    ----------------------------------------------

    '''
    try :
        http_method = event['httpMethod'] if 'httpMethod' in event else ''
        common_log.output(
            common_log.LOG_INFO
            ,'START'
            ,event
            ,http_method
            ,100
        )
        common_log.output(
            common_log.LOG_DEBUG
            ,event
            ,event
            ,http_method
            ,101
        )
        #初期処理
        param_dict, param_record = init(event)
        common_log.output(common_log.LOG_DEBUG, param_dict,event,http_method,101)
        common_log.output(common_log.LOG_DEBUG, param_record,event,http_method,102)
        # 返却ヘッダ設定
        ret_dict = get_response(param_dict)
        # メイン処理実行
        if http_method == 'POST' :
            ret_dict = post_main(param_dict, param_record, ret_dict)
        elif http_method == 'DELETE' :
            ret_dict = delete_main(param_dict, param_record, ret_dict)
        elif http_method == 'PUT' :
            ret_dict = put_main(param_dict, param_record, ret_dict)
        common_log.output(common_log.LOG_DEBUG, param_record,event,http_method,103)
        return ret_dict
    except :
        traceback.print_exc()
        print('例外発生')
        return

