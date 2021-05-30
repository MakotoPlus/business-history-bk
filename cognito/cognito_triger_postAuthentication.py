#--------------------------------------------------------------
# cognito_triger_postAuthentication
# ユーザアカウントログイン処理
#
# ユーザ姓名を取得しCognito情報から更新処理と、最終ログイン情報を更新する
#
#
#--------------------------------------------------------------

import json,os,boto3
import traceback
import common_log
import common_const
import common_util
from typing import Tuple

GIVEN_NAME ='given_name'
FAMILY_NAME = 'family_name'

def init(event) -> Tuple[dict, dict]:
    '''
    初期処理

    Parameters
    ----------------------------------------------
    event : dict
        Lambda実行時パラメータ

    Returns
    ----------------------------------------------

    '''
    param_dict = common_util.get_env()
    param_record = {}
    # パラメータ取得
    param_record[common_const.PARAM_USERID] = event['request']['userAttributes']['sub']
    param_record[GIVEN_NAME] = event['request']['userAttributes'][GIVEN_NAME]
    param_record[FAMILY_NAME] = event['request']['userAttributes'][FAMILY_NAME]
    param_record['full_name'] = '{0} {1}'.format( param_record['family_name'], param_record['given_name'])
    param_record['last_login'] = common_util.get_datetime()

    return param_dict, param_record

def main(param_dict, param_record, event, ret_dict ) -> dict :
    '''
    メイン関数

    Parameters
    ----------------------------------------------
    param_dict : dict
        初期情報格納dict
    param_record : dict
        更新用パラメータ
    Returns
    ----------------------------------------------
    '''
    try:
        common_log.output(common_log.LOG_INFO,'START' ,event,'main', 1)
        if param_dict[common_const.DYNAMODB_ENDPOINT]:
            common_log.output(common_log.LOG_INFO,
            'endpoint url={0} '.format(param_dict[common_const.DYNAMODB_ENDPOINT]),
            event, 'main', 2)
            dynamodb = boto3.resource('dynamodb', 
                endpoint_url=param_dict[common_const.DYNAMODB_ENDPOINT])
        else:
            common_log.output(common_log.LOG_INFO,
                'endpoint url=Nothing',event, 'main', 3)
            dynamodb = boto3.resource('dynamodb')
        #---------------------------------------------------
        # データ取得
        table_m_user = dynamodb.Table(param_dict[common_const.ENV_M_USER])
        common_log.output(common_log.LOG_DEBUG,
            'get_item uuid:{0}'.format(param_record[common_const.PARAM_USERID]),event, 'main', 4)
        response = table_m_user.get_item(Key={'uuid':param_record[common_const.PARAM_USERID]})
        if False == ('Item' in response):
            errmsg = {
                'message': '{0}:{1}'.format(
                    common_const.ERROR_NO_USERID
                    ,param_record[common_const.PARAM_USERID]
                    )
            }
            ret_dict['body'] = json.dumps(errmsg)
            ret_dict['statusCode'] = common_const.ERROR_REQUEST
            return ret_dict
        #---------------------------------------------------
        # データ更新
        # パラメータ情報で更新
        user_dict = response['Item'];
        table_m_user.update_item(
            Key = { 
                'uuid' : user_dict['uuid']
            }
            ,UpdateExpression = 'set full_name=:full_name '    \
                ', family_name=:family_name, given_name=:given_name '    \
                ', last_login=:last_login'
            ,ExpressionAttributeValues = {
                ':full_name' : param_record['full_name']
                ,':family_name': param_record['family_name']
                ,':given_name': param_record['given_name']
                ,':last_login': param_record['last_login']
            }
            ,ReturnValues = "UPDATED_NEW"
        )
        ret_dict['statusCode'] = common_const.SUCCESS_CODE
        return ret_dict
    except:
        common_log.output(common_log.LOG_ERROR,'メイン処理で例外発生' ,event,'main', 5)
        #print( e.args)
        traceback.print_exc()
        errmsg = {
            'message': common_const.ERROR_MESSAGE_001
        }
        ret_dict['body'] = json.dumps(errmsg)
        ret_dict['statusCode'] = common_const.ERROR_REQUEST
        return ret_dict    

def run(event, context):
    try:
        print('start')
        common_log.output(
            common_log.LOG_INFO
            ,'START'
            ,event
            ,'run'
            ,1
        )
        print(event)
        common_log.output(common_log.LOG_INFO,'初期処理開始', event, 'run', 1 )
        param_dict, param_record = init(event)
        print(param_dict)
        print(param_record)
        # メイン処理実行
        ret_dict = {}
        ret_dict = main(param_dict, param_record, event, ret_dict)
        #print(context);
        #add_user(event['request']['userAttributes'])
        common_log.output(common_log.LOG_INFO,'正常終了', event, 'run', 9 )
        return event
    except:
        traceback.print_exc()
        common_log.output(common_log.LOG_ERROR,'異常終了', event, 'run', 9 )
        return {}


