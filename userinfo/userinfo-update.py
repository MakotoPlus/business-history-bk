#--------------------------------------------------------------
# userinfo-update
# ユーザアカウント情報変更
#
# url:/userinfo/{userid}
# method:put
#
#--------------------------------------------------------------
import os
import json
import boto3
import ast
from boto3.dynamodb.conditions import Key

ENV_ACCESS_CONTROL_ALLOW_ORIGIN = 'ACCESS_CONTROL_ALLOW_ORIGIN'
ENV_M_USER = 'TABLE_M_USER'
PARAM_USERID = 'uuid'
ERROR_MESSAGE = 'サーバエラーが発生しました'
ERROR_NO_USERID = 'ERROR_NO_USERID'
DYNAMODB_ENDPOINT='DYNAMODB_ENDPOINT'

SUCCESS_CODE = 200
ERROR_REQUEST = 400
ERROR_INTERNAL = 500

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
    param_dict[ENV_ACCESS_CONTROL_ALLOW_ORIGIN] = os.environ[ENV_ACCESS_CONTROL_ALLOW_ORIGIN]
    param_dict[ENV_M_USER] = os.environ[ENV_M_USER]
    param_dict[DYNAMODB_ENDPOINT] = os.environ[DYNAMODB_ENDPOINT]
    return param_dict

def init(event) -> (dict, dict):
    '''
    初期処理

    Parameters
    ----------------------------------------------
    event : dict
        Lambda実行時パラメータ

    Returns
    ----------------------------------------------
        処理利用データ : dict
        更新inputデータ : dict
    '''
    print('get_env start')
    param_dict = get_env()
    # パラメータ取得
    param_dict[PARAM_USERID] = event['pathParameters'][PARAM_USERID]
    # ENV_ACCESS_CONTROL_ALLOW_ORIGINの値をevent['headers']['origin']が設定されていた場合は
    # 入替て設定する
    print(param_dict[PARAM_USERID])
    if 'origin' in event['headers']:
        print('set headers origin')
        param_dict[ENV_ACCESS_CONTROL_ALLOW_ORIGIN] = event['headers']['origin']    
    #print('JSON')
    #print(json.loads(event['body'].encode('utf-8')))
    #print(json.loads(event['body']))
    #print('literal_eval')
    #print(ast.literal_eval(event['body']))
    param_record = ast.literal_eval(event['body']);
    #param_record = json.loads(event['body']);
    param_record['full_name'] = '{0} {1}'.format( param_record['family_name'], param_record['given_name'])

    print('param_record-full_name')
    print(param_record['full_name'])
    return param_dict, param_record

def get_response(param_dict) -> dict :
    return {
        'headers': {
            #'Content-Type': 'application/json'
            # CORS設定 '*' だけで動いたけどとりあえず設定しておく
            #
            # 'Access-Control-Allow-Origin': '*'  
            #,'Vary':'Origin'
            'Access-Control-Allow-Origin': param_dict[ENV_ACCESS_CONTROL_ALLOW_ORIGIN]
            ,'Access-Control-Allow-Methods':'GET, PUT, DELETE, OPTIONS'
            ,'Access-Control-Allow-Headers':'X-Requested-With, X-HTTP-Method-Override, Content-Type, Accept'
            ,'Access-Control-Allow-Credentials':'true'
        }
        ,'isBase64Encoded': False
    }        

def get_records(table, **kwargs):
    while True:
        response = table.scan(**kwargs)
        for item in response['Items']:
            yield item
        if 'LastEvaluatedKey' not in response:
            break
        kwargs.update(ExclusiveStartKey=response['LastEvaluatedKey'])

def main(param_dict, param_record, ret_dict ) -> dict :
    '''
    メイン関数

    Parameters
    ----------------------------------------------
    param_dict : dict
        初期情報格納dict
    param_record : dict
        更新用パラメータ
    ret_dict : dict
        返却用のdict
    Returns
    ----------------------------------------------
    '''
    try:
        print('主処理')
        if param_dict[DYNAMODB_ENDPOINT]:
            print('endpoint url={0} '.format(param_dict[DYNAMODB_ENDPOINT]))
            dynamodb = boto3.resource('dynamodb', endpoint_url=param_dict[DYNAMODB_ENDPOINT])
        else:
            print('endpoint url=Nothing')
            dynamodb = boto3.resource('dynamodb')

        #---------------------------------------------------
        # 全件データ取得
        #records = get_records(
        #    dynamodb.Table(param_dict[ENV_M_USER])
        #)
        #
        #for record in records:
        #    print('----------------------------')
        #    print(record)
        #print('----------------------------')

        #---------------------------------------------------
        # データ取得
        table_m_user = dynamodb.Table(param_dict[ENV_M_USER])
        #response = table_m_user.query(
        #    KeyConditionExpression=Key('uuid').eq(param_dict[PARAM_USERID])
        #)
        print('get_item uuid:{0}'.format(param_dict[PARAM_USERID]))
        response = table_m_user.get_item(Key={'uuid':param_dict[PARAM_USERID]})
        print(response)
        if False == ('Item' in response):
            errmsg = {
                'message': '{0}:{1}'.format(
                    ERROR_NO_USERID
                    ,param_dict[PARAM_USERID]
                    )
            }
            ret_dict['body'] = json.dumps(errmsg)
            ret_dict['statusCode'] = ERROR_REQUEST
            return ret_dict

        #---------------------------------------------------
        # データ更新
        # パラメータ情報で更新
        user_dict = response['Item'];
        print('year')
        print(type(param_record['birthday']['year']))
        print(param_record['birthday']['year'])

        ######################################
        # キーではなくなったのでコメントアウト
        # UPDATE すると両方のDICTが更新されてしまうため、事前にFULL_NAMEを取得して置く
        #full_name = response['Item']['full_name']
        #user_dict.update(param_record)

        table_m_user.update_item(
            Key = { 
                'uuid' : user_dict['uuid']
            }
            ,UpdateExpression = 'set full_name=:full_name '    \
                ', family_name=:family_name, given_name=:given_name '    \
                ', family_name_kana=:family_name_kana, given_name_kana=:given_name_kana '    \
                ', sex=:sex, train=:train '    \
                ', station=:station, date_joined=:date_joined'   \
                ', initial=:initial, address=:address'   \
                ', pr=:pr, qualifications=:qualifications'   \
                ', birthday=:birthday'   \
#                    ', birthday.year=:year'   \
#                    ', birthday.month=:month'   \
#                    ', birthday.day=:day'
            ,ExpressionAttributeValues = {
                ':full_name' : param_record['full_name']
                ,':family_name': param_record['family_name']
                ,':given_name': param_record['given_name']
                ,':family_name_kana': param_record['family_name_kana']
                ,':given_name_kana': param_record['given_name_kana']
                ,':sex': param_record['sex']
                ,':train': param_record['train']
                ,':station': param_record['station']
                ,':date_joined': param_record['date_joined']
                ,':initial': param_record['initial']
                ,':address': param_record['address']
                ,':pr': param_record['pr']
                ,':qualifications': param_record['qualifications']
                ,':birthday': param_record['birthday']
#                    ,':year': str(param_record['birthday']['year'])
#                    ,':month': str(param_record['birthday']['month'])
#                    ,':day': str(param_record['birthday']['day'])
            }
            ,ReturnValues = "UPDATED_NEW"
        )
        ret_dict['body'] = json.dumps(param_record)
        ret_dict['statusCode'] = SUCCESS_CODE
        return ret_dict
    except:
        print('メイン処理で例外発生')
        #print( e.args)
        import traceback
        traceback.print_exc()
        errmsg = {
            'message': ERROR_MESSAGE
        }
        ret_dict['body'] = json.dumps(errmsg)
        ret_dict['statusCode'] = ERROR_REQUEST
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
        print(event)
        #初期処理
        print('初期処理')
        param_dict, param_record = init(event)
        print('パラメータ情報')
        print(param_dict)    
        # 返却ヘッダ設定
        ret_dict = get_response(param_dict)
        # メイン処理実行
        ret_dict = main(param_dict, param_record, ret_dict)
        print(ret_dict)
        return ret_dict
    except:
        print('初期処理で例外発生')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print('start')

    FILENAME="test_data.json"
    os.environ[ENV_M_USER] = 'm_user'
    os.environ[ENV_ACCESS_CONTROL_ALLOW_ORIGIN]='test'

    #ファイル読込
    data = {}
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), FILENAME)
        , mode='r', encoding="utf_8") as fd:
        data = json.load(fd)
    print(data)
    print(run(data, None))


