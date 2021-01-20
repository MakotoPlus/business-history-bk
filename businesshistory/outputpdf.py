import boto3	
import os,io,sys,base64,json
import uuid	
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

def run(event, context):
    print( 'Start Lambda run()')
    print( event )
    origin_value = os.environ['ACCESS_CONTROL_ALLOW_ORIGIN']

    # バイナリデータを取得しエンコードを実施する
    #
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