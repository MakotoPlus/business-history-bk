import boto3	
import os,io,sys,base64,json
import uuid	
import traceback
from datetime import datetime
from decimal import Decimal
from boto3.dynamodb.conditions import Key
import common_log
import common_const
import common_util
from typing import List, Tuple

#import report01
from businesshistory import report01
#from businesshistory import report01
#from ...report import report01
#from lib.report01 import BusinessHistoryReport
#from ..lib.report01 import BusinessHistoryReport

key_name = '51.pdf'
#key_name = '52.txt'

#def resize_image(image_path, resized_path):	//Pillowの機能を使用した画像データ処理用関数
#    with Image.open(image_path) as image:	//画像ファイルから画像データを取得
#        image.thumbnail(tuple(x / 2 for x in image.size)	//画像データサイズを1/2に縮小
#        image.save(resized_path)	//Lambda内の一時保存先に保存
def init(event, http_method) -> Tuple[dict, dict, List]:
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

    method = 'init'

    # ENV_ACCESS_CONTROL_ALLOW_ORIGINの値をevent['headers']['origin']が設定されていた場合は
    # 入替て設定する
    if 'origin' in event['headers']:
        print('set headers origin')
        param_dict[common_const.ENV_ACCESS_CONTROL_ALLOW_ORIGIN] = event['headers']['origin']
    
    http_method = event['httpMethod'] if 'httpMethod' in event else ''
    if http_method != 'POST':
        common_log.output(
            common_log.LOG_ERROR
            ,f'Method Error={http_method}'
            ,None
            ,method
            ,202
        )
        return param_dict, None, None

    param_body = json.loads(event['body'])
    param_printinf = param_body['printinf']
    param_userlist = param_body['uuid']
    return param_dict, param_printinf, param_userlist

def create_userdata(param_dict, param_printinf, userid) -> dict:
    '''
    印刷ユーザデータ作成関数

    Parameters
    ----------------------------------------------
    param_dict : dict
        初期情報格納dict
    param_printinf : dict
        印刷情報
    userid : str
        ユーザID
    Returns
    ----------------------------------------------
    dict
    '''
    method = 'create_userdata'
    try:
        common_log.output(common_log.LOG_INFO, 'START' ,None ,method ,501)
        if param_dict[common_const.DYNAMODB_ENDPOINT]:
            print('endpoint url={0} '.format(param_dict[common_const.DYNAMODB_ENDPOINT]))
            dynamodb = boto3.resource('dynamodb', endpoint_url=param_dict[common_const.DYNAMODB_ENDPOINT])
        else:
            print('endpoint url=Nothing')
            dynamodb = boto3.resource('dynamodb')
        #
        # ユーザ情報取得
        table_m_user = dynamodb.Table(param_dict[common_const.ENV_M_USER])
        response = table_m_user.get_item(Key={"uuid": userid})
        if 'Item' not in response :
            common_log.output(common_log.LOG_ERROR, 'USERID Nothing' ,None ,method ,502)
            common_log.output(common_log.LOG_ERROR, response ,None ,method ,503)
            return None

        userdata = response['Item']
        birthday = f"{userdata['birthday']['year']}/{userdata['birthday']['month']}/{userdata['birthday']['day']}"
        ret_data ={
            report01.key_usrname : userdata['full_name']
            ,report01.key_usrname_kana : userdata['family_name_kana'] + ' ' + userdata['given_name_kana']
            ,report01.key_username_initial : userdata['initial']
            ,report01.key_birthday : birthday
            ,report01.key_gender : userdata['sex']
            ,report01.key_train : userdata['train']
            ,report01.key_station : userdata['station']
            ,report01.key_address : userdata['address']
            ,report01.key_educational_background : userdata['date_joined']
            ,report01.key_qualification : userdata['qualifications']
            ,report01.key_pr : userdata['pr']
        }
        return ret_data
    except Exception as ex:
        print(f'{method}で例外発生')
        traceback.print_exc()
        raise ex

def create_companydata(param_dict, param_printinf, userid) -> dict:
    '''
    企業データ作成関数

    Parameters
    ----------------------------------------------
    param_dict : dict
        初期情報格納dict
    param_printinf : dict
        印刷情報
    userid : str
        ユーザID
    Returns
    ----------------------------------------------
    dict
    '''
    method = 'create_companydata'
    try:
        common_log.output(common_log.LOG_INFO, 'START' ,None ,method ,601)

        if False == param_printinf['is_company']:
            return {}        

        if param_dict[common_const.DYNAMODB_ENDPOINT]:
            print('endpoint url={0} '.format(param_dict[common_const.DYNAMODB_ENDPOINT]))
            dynamodb = boto3.resource('dynamodb', endpoint_url=param_dict[common_const.DYNAMODB_ENDPOINT])
        else:
            print('endpoint url=Nothing')
            dynamodb = boto3.resource('dynamodb')
        #
        # 企業情報取得
        table_m_company = dynamodb.Table(param_dict[common_const.ENV_M_COMPANY])
        response = table_m_company.get_item(
            Key={"companycd": int(param_printinf['companycd']), "uuid": userid})
        if 'Item' not in response:
            common_log.output(common_log.LOG_INFO, 'COMPANY Nothing' ,None ,method ,602)
            return None
        company_data = response['Item']

        address = company_data['address_1']
        if 'address_2' in company_data:
            address = address + company_data['address_2']
        if 'address_3' in company_data:
            address = address + company_data['address_3']

        ret_data ={
            report01.key_company : company_data['company_name'] if 'company_name' in company_data else '',
            report01.key_company_address : company_data['address'] if 'address' in company_data else '',
            report01.key_company_tel : company_data['tel'] if 'tel' in company_data else '',
            report01.key_company_fax : company_data['fax'] if 'fax' in company_data else '',
            report01.key_company_url : company_data['hp'] if 'hp' in company_data else '',
        }
        return ret_data
    except Exception as ex:
        print(f'{method}で例外発生')
        traceback.print_exc()
        raise ex

def create_historydata(param_dict, param_printinf, userid) -> dict:
    '''
    業務経歴データ作成関数

    Parameters
    ----------------------------------------------
    param_dict : dict
        初期情報格納dict
    param_printinf : dict
        印刷情報
    userid : str
        ユーザID
    Returns
    ----------------------------------------------
    dict
    '''
    method = 'create_historydata'
    try:
        common_log.output(common_log.LOG_INFO, 'START' ,None ,method ,701)
        if param_dict[common_const.DYNAMODB_ENDPOINT]:
            print('endpoint url={0} '.format(param_dict[common_const.DYNAMODB_ENDPOINT]))
            dynamodb = boto3.resource('dynamodb', endpoint_url=param_dict[common_const.DYNAMODB_ENDPOINT])
        else:
            print('endpoint url=Nothing')
            dynamodb = boto3.resource('dynamodb')

        #
        # 業務経歴データ取得
        table_t_work_history = dynamodb.Table(param_dict[common_const.ENV_T_WORK_HISTORY])
        responses = table_t_work_history.query(
            KeyConditionExpression=Key('uuid').eq(userid)
            ,ScanIndexForward = False)
        common_log.output(common_log.LOG_DEBUG,responses, None,'main', 702)
        result_list = []
        if 'Items' not in responses:
            return result_list
        history_datas = responses['Items']
        for index  in  range(len(history_datas)):
            history = {
                report01.key_hist_no : index + 1,
                report01.key_hist_start_date : f"{history_datas[index]['work_from']}/01",
                report01.key_hist_end_date : f"{history_datas[index]['work_to']}/01",
                report01.key_hist_industry : history_datas[index]['industry'] if 'industry' in history_datas[index] else '',
                report01.key_hist_system : history_datas[index]['jobname'] if 'jobname' in history_datas[index] else '',
                report01.key_hist_scale : str(history_datas[index]['scale']) if 'scale' in history_datas[index] else '',
                report01.key_hist_position : str(history_datas[index]['position']) if 'position' in history_datas[index] else '',
                report01.key_hist_number_pepole : history_datas[index]['persons'] if 'persons' in history_datas[index] else '',
                report01.key_hist_detail : history_datas[index]['details'] if 'details' in history_datas[index] else '',
            }
            #
            # 工程設定 値がTrueのみ設定
            process = []            
            for key in history_datas[index]['process_group_list']:
                if history_datas[index]['process_group_list'][key] == True :
                    process.append(key)
            history[report01.key_process] = process
            #
            # 環境
            # 1.言語
            lang_dict = get_envdict('言語', history_datas[index]['envGroups'])
            # 2.F/W
            fw_dict = get_envdict('F/W', history_datas[index]['envGroups'])
            # 3.OS
            os_dict = get_envdict('OS', history_datas[index]['envGroups'])
            # 4.DB
            db_dict = get_envdict('DB', history_datas[index]['envGroups'])
            technology = {
                report01.key_language : lang_dict
                ,report01.key_fw : fw_dict
                ,report01.key_os : os_dict
                ,report01.key_db : db_dict
            }
            history[report01.key_technology] = technology
            result_list.append(history)
        return result_list
    except Exception as ex:
        print(f'{method}で例外発生')
        traceback.print_exc()
        raise ex

def get_envdict(typeName, envs) -> dict:
    '''
    指定されたキー名で存在する typeを見つけ出し, detailsをキー名にしてversionを値のdictにして返す
    '''
    ret_dict = {}    
    for index in  range(len(envs)):
        if ('type' not in envs[index]) or ('details' not in envs[index]) or ('version' not in envs[index]):
            continue
        if typeName != envs[index]['type']:
            continue
        ret_dict[envs[index]['details']] = envs[index]['version']
    return ret_dict
    



def post_main(param_dict, param_printinf, param_userlist, ret_dict) -> dict:
    '''
    メイン関数

    Parameters
    ----------------------------------------------
    param_dict : dict
        初期情報格納dict
    param_printinf : dict
        印刷情報
    param_userlist : list
        ユーザIDリスト
    Returns
    ----------------------------------------------
    '''
    method = 'post_main'

    try :
        common_log.output(common_log.LOG_INFO, 'START' ,None ,method ,401)

        #
        # req dict作成
        req = {
            'out_name_type' : param_printinf['out_name_type'],
            'output_date' : param_printinf['output_date'],
        }

        #
        # 企業情報データ取得
        company_data = {}
        common_log.output(common_log.LOG_DEBUG, f"is_company={param_printinf['is_company']}", None ,method ,402)
        if param_printinf['is_company']:
            company_data = create_companydata(param_dict, param_printinf, param_userlist[0])

        #
        # ユーザ情報データ取得
        user_datas = []
        for userid in param_userlist :
            # 1ユーザ分のデータを取得
            user_data = {}
            user_data = create_userdata( param_dict, param_printinf, userid)
            if user_data is None :
                # エラー発生
                return None
            #ユーザデータに企業情報追加
            user_data = { **user_data, **company_data}
            # 1ユーザ分の業務経歴データ取得
            user_data['history'] = create_historydata(param_dict, param_printinf, userid)
            user_datas.append(user_data)

        bytes_buffer = io.BytesIO()
        for user_data in user_datas :
            print_dict = {
                'req' : req
                ,'data' : user_data
            }
            common_log.output(common_log.LOG_DEBUG, "BusinessHistoryReport Call", None ,method ,403)
            common_log.output(common_log.LOG_DEBUG, print_dict, None ,method ,404)
            reportObj = report01.BusinessHistoryReport(bytes_buffer)
            reportObj.output(print_dict)

        byte_value = bytes_buffer.getvalue()
        encode_string = base64.b64encode(byte_value).decode()
        ret_dict['body'] = json.dumps(encode_string)
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
        ,'isBase64Encoded': True
    }        

def run(event, context):
    '''
    処理開始関数

    PDF出力

    Parameters
    ----------------------------------------------
    event : dict
    context : dict

    Returns
    ----------------------------------------------

    '''
    print( 'Start Lambda run()')
    print( event )
    origin_value = os.environ['ACCESS_CONTROL_ALLOW_ORIGIN']

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
        param_dict, param_printinf, param_userlist = init(event, http_method)
        common_log.output(common_log.LOG_DEBUG, param_dict, event, http_method, 101)
        common_log.output(common_log.LOG_DEBUG, param_printinf, event, http_method, 102)
        common_log.output(common_log.LOG_DEBUG, param_userlist, event, http_method, 103)
        if param_printinf is None :
            ret_dict = {}
            errmsg = {
                'message': common_const.ERROR_MESSAGE_002
            }
            ret_dict['body'] = json.dumps(errmsg)
            ret_dict['statusCode'] = common_const.ERROR_REQUEST
            return ret_dict
        # 返却ヘッダ設定
        ret_dict = get_response(param_dict)
        #
        # PDF Output Joson取得
        ret_dict = post_main(param_dict, param_printinf, param_userlist, ret_dict)
        common_log.output(common_log.LOG_DEBUG, ret_dict, event, http_method, 104)
        return ret_dict

    except :
        traceback.print_exc()
        print('例外発生')
        return

'''

    # バイナリデータを取得しエンコードを実施する
    #
    if isinstance(event['body'], dict):
        body_dict = event['body']
    else:
        body_dict = json.loads(event['body'])
    print('message key is ', ('message' in body_dict ))
    if False == ('message' in body_dict ):
        response = {
            "headers": {
                # CORS設定
                #"Access-Control-Allow-Origin": "*"  
                "Access-Control-Allow-Origin": origin_value
            }
            ,"statusCode": 400,
            "body": "no message key",
        }
        return response

    #print(event['body'][0]['message'])
    bytes_buffer = io.BytesIO()
    pdfObj = report01.BusinessHistoryReport(bytes_buffer)
    #jsonObj = event['body'][0]['message']
    jsonObj = body_dict['message']
    print('jsonObj', type(jsonObj))
    print('jsonObj Data', jsonObj)
    pdfObj.output(jsonObj)
    #client.download_fileobj(Bucket=backet_name, Key=key_name, Fileobj=bytes_buffer)
    byte_value = bytes_buffer.getvalue()
    encode_string = base64.b64encode(byte_value).decode()
    #---------------------------------------------------------------
    #
    print('pdf_obj OK---------------------Encode Buffer Start')
    print(json.dumps(encode_string))
    print('pdf_obj OK---------------------Encode Buffer End')
    response = {
        "headers": {
            "Content-Type": "application/pdf",
            # CORS設定
            #"Access-Control-Allow-Origin": "*"  
            "Access-Control-Allow-Origin": origin_value
        }
        ,"statusCode": 200,
        "body": json.dumps(encode_string),
        "isBase64Encoded" : True, 
    }
    return response
'''



'''
def run(event, context):
    print( 'Start Lambda run()')
    print( event['message'] )
    backet_name = os.environ['S3_BUCKET']
    # S3にあるファイルを読込
    s3_io = boto3.resource('s3')
    client = boto3.client('s3')
    # バイナリデータを取得しエンコードを実施する
    #
    bytes_buffer = io.BytesIO()
    client.download_fileobj(Bucket=backet_name, Key=key_name, Fileobj=bytes_buffer)
    byte_value = bytes_buffer.getvalue()
    encode_string = base64.b64encode(byte_value).decode()
    #---------------------------------------------------------------
    #
    print('pdf_obj OK---------------------Encode Buffer Start')
    print(json.dumps(encode_string))
    print('pdf_obj OK---------------------Encode Buffer End')
    response = {
        "headers": {
            "Content-Type": "application/pdf",
            # CORS設定
            #"Access-Control-Allow-Origin": "*"  
            "Access-Control-Allow-Origin":  "https://cl-business-history.s3-ap-northeast-1.amazonaws.com"            
        }
        ,"statusCode": 200,
        "body": json.dumps(encode_string),
        "isBase64Encoded" : True, 
    }
    return response
'''