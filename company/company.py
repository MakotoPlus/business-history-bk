#--------------------------------------------------------------
# company.py
# 企業情報処理
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

def init(event, http_method) -> Tuple[dict, dict]:
    '''
    初期処理

    Parameters
    ----------------------------------------------
    event : dict
        Lambda実行時パラメータ
    http_method : str
        POST, GET

    Returns
    ----------------------------------------------
    param_dict 
        パラメータから取得した情報を格納
    param_record
        DBに登録する情報(パラメータ['body']の情報 + ユーザID)
    '''

    method = 'init'
    common_log.output(
        common_log.LOG_INFO
        ,'start'
        ,None
        ,method
        ,201
    )

    #環境情報取得    
    param_dict = common_util.get_env()
    # パラメータ取得
    if 'origin' in event['headers']:
        param_dict[common_const.ENV_ACCESS_CONTROL_ALLOW_ORIGIN] = event['headers']['origin']
    # ユーザID取得
    param_dict[common_const.PARAM_USERID] = event['pathParameters'][common_const.PARAM_USERID]
    # 企業CD取得
    param_dict[common_const.PARAM_COMPANYCD] = event['pathParameters'][common_const.PARAM_COMPANYCD]

    method = 'init'
    common_log.output(
        common_log.LOG_INFO
        ,f'USERID: ${param_dict[common_const.PARAM_USERID]} COMPANYCD:${param_dict[common_const.PARAM_COMPANYCD]}'
        ,None
        ,method
        ,202
    )
    # ENV_ACCESS_CONTROL_ALLOW_ORIGINの値をevent['headers']['origin']が設定されていた場合は
    # 入替て設定する
    if 'origin' in event['headers']:
        print('set headers origin')
        param_dict[common_const.ENV_ACCESS_CONTROL_ALLOW_ORIGIN] = event['headers']['origin']    
    
    http_method = event['httpMethod'] if 'httpMethod' in event else ''
    param_record = {}

    if http_method == 'PUT':
        common_log.output(
            common_log.LOG_INFO
            ,event['body']
            ,None
            ,method
            ,202
        )
        param_record = json.loads(event['body'])
    param_record[common_const.PARAM_USERID]=param_dict[common_const.PARAM_USERID]
    param_record[common_const.PARAM_COMPANYCD]=param_dict[common_const.PARAM_COMPANYCD]
    return param_dict, param_record

def get_m_company_table(param_dict):
    '''
    パラメータ内容からM_COMPANY_TABLEのリソースを返す
    '''
    if param_dict[common_const.DYNAMODB_ENDPOINT]:
        print('endpoint url={0} '.format(param_dict[common_const.DYNAMODB_ENDPOINT]))
        dynamodb = boto3.resource('dynamodb', endpoint_url=param_dict[common_const.DYNAMODB_ENDPOINT])
    else:
        print('endpoint url=Nothing')
        dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table(param_dict[common_const.ENV_M_COMPANY])

def put_main(param_dict, param_record, ret_dict ) -> dict :
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
    method = 'put_main'
    try :
        common_log.output(
            common_log.LOG_INFO
            ,f'COMPANYCD:{param_record[common_const.PARAM_COMPANYCD]} USERID:{param_record[common_const.PARAM_USERID]}'
            ,None
            ,method
            ,401
        )
        common_log.output(
            common_log.LOG_DEBUG
            ,param_dict
            ,None
            ,method
            ,402
        )
        common_log.output(
            common_log.LOG_DEBUG
            ,param_record
            ,None
            ,method
            ,403
        )
        # 登録日付を設定
        # 設定されていたら何もしない
        s_datetime = common_util.get_datetime();
        if common_const.ENV_COLUMN_INSERT_DATE in param_record :
            if '' == param_record[common_const.ENV_COLUMN_INSERT_DATE]:
                param_record[common_const.ENV_COLUMN_INSERT_DATE] = s_datetime
        else:
            param_record[common_const.ENV_COLUMN_INSERT_DATE] = s_datetime
        # 更新日付を設定
        param_record[common_const.ENV_COLUMN_UPDATE_DATE] = s_datetime
        table_m_compay = get_m_company_table(param_dict);
        #企業コードを数値型変換
        param_record[common_const.PARAM_COMPANYCD] = int(param_record[common_const.PARAM_COMPANYCD]);
        response = table_m_compay.put_item(Item = param_record)
        common_log.output(common_log.LOG_INFO, response, None, method, 403)
        ret_dict['statusCode'] = common_const.SUCCESS_CODE
        return ret_dict
    except:
        print(f'{method}で例外発生')
        traceback.print_exc()
        errmsg = {
            'message': common_const.ERROR_MESSAGE_001
        }
        ret_dict['body'] = json.dumps(errmsg)
        ret_dict['statusCode'] = common_const.ERROR_REQUEST
        return ret_dict    


def get_main(param_dict, param_record, ret_dict ) -> dict :
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
    method = 'get_main'
    try :

        if (param_record[common_const.PARAM_COMPANYCD] != "0"):
            param_record[common_const.PARAM_USERID] = "0";

        common_log.output(
            common_log.LOG_INFO
            ,f'COMPANYCD:{param_record[common_const.PARAM_COMPANYCD]} USERID:{param_record[common_const.PARAM_USERID]}'
            ,None
            ,method
            ,301
        )

        table_m_compay = get_m_company_table(param_dict);
        response = table_m_compay.get_item(
            Key={"companycd" : int(param_record[common_const.PARAM_COMPANYCD]),
                "uuid" : param_record[common_const.PARAM_USERID]
            }
        )
        common_log.output(
            common_log.LOG_DEBUG
            ,response
            ,None
            ,method,302
        )
        ret_dict['body'] = json.dumps(response['Item'], default=common_util.jsondumps_custom_proc)
        ret_dict['statusCode'] = common_const.SUCCESS_CODE
        return ret_dict
    except:
        print(f'{method}で例外発生')
        traceback.print_exc()
        errmsg = {
            'message': common_const.ERROR_MESSAGE_001
        }
        ret_dict['body'] = json.dumps(errmsg)
        ret_dict['statusCode'] = common_const.ERROR_REQUEST
        return ret_dict    

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

def run(event, context) :
    '''
    処理開始関数

    企業情報処理

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
        param_dict, param_record = init(event, http_method)
        common_log.output(common_log.LOG_DEBUG, param_dict,event,http_method,101)
        common_log.output(common_log.LOG_DEBUG, param_record,event,http_method,102)
        if (http_method != 'GET') and (http_method != 'PUT'):
            ret_dict = {}
            errmsg = {
                'message': common_const.ERROR_MESSAGE_002
            }
            ret_dict['body'] = json.dumps(errmsg)
            ret_dict['statusCode'] = common_const.ERROR_REQUEST
            return ret_dict
        # 返却ヘッダ設定
        ret_dict = get_response(param_dict)
        # メイン処理実行
        if http_method == 'GET' :
            ret_dict = get_main(param_dict, param_record, ret_dict)
        #elif http_method == 'DELETE' :
        #    ret_dict = delete_main(param_dict, param_record, ret_dict)
        elif http_method == 'PUT' :
            ret_dict = put_main(param_dict, param_record, ret_dict)
        common_log.output(common_log.LOG_DEBUG, param_record,event,http_method,103)
        return ret_dict
    except :
        traceback.print_exc()
        print('例外発生')
        return

