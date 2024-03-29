import boto3	
import os,io,sys,base64,json
import uuid	


key_name = '51.pdf'
#key_name = '52.txt'

#def resize_image(image_path, resized_path):	//Pillowの機能を使用した画像データ処理用関数
#    with Image.open(image_path) as image:	//画像ファイルから画像データを取得
#        image.thumbnail(tuple(x / 2 for x in image.size)	//画像データサイズを1/2に縮小
#        image.save(resized_path)	//Lambda内の一時保存先に保存


def run(event, context):

    print( 'Start Lambda run()')
    print( event )
    backet_name = os.environ['S3_BUCKET']

    # S3にあるファイルを読込
    s3_io = boto3.resource('s3')
    client = boto3.client('s3')
    bucket = s3_io.Bucket(backet_name)
    result = bucket.meta.client.list_objects(Bucket=bucket.name, Delimiter='/')
    for o in result.get('Contents'):
        print(o.get('Key'))

    print( 'File Read')
    print('KeyName=', key_name)
    #object = s3_io.get_object(Bucket=backet_name, Key=key_name)    
    #s3object = bucket.Object(key_name)
    #s3object = s3_io.Object(backet_name, key_name).get()

    #print('type=', type(s3object))
    #print('ContentType ->' + str(object.get('ContentType')))
    #print('ContentLength ->' + str(object.get('ContentLength')))

    #client.download_file(bucket, key, download_path)

    body = {
        "message": "successfully!",
        "input": event
    }

    #pdf_obj = base64.b64encode(io.BytesIO(s3object['Body'].read()))
    #pdf_obj = io.BytesIO(s3object['Body'].read())
    #encode_string = base64.b64encode(pdf_obj).decode('utf-8')

    #
    # S3 client.download_fileobjでFileobjを io.ByteIO()のハンドルを渡すことでデータ読込んで
    # バイナリデータを取得しエンコードを実施する
    #
    print('Read')
    #print(s3object['Body'])
    bytes_buffer = io.BytesIO()

    
    client.download_fileobj(Bucket=backet_name, Key=key_name, Fileobj=bytes_buffer)
    byte_value = bytes_buffer.getvalue()
    #encode_string = base64.b64encode(byte_value).decode('utf-8')
    encode_string = base64.b64encode(byte_value).decode()
    '''
    'Body'がStremなんちゃらでBinaryではないらしく下記コードでは上手くデータ取得が出来なかった
    print('read Type', type(io.BytesIO(s3object['Body']).read()))
    print('read -1 Type', type(io.BytesIO(s3object['Body']).read(-1)))
    print('getbuffer Type', type(io.BytesIO(s3object['Body']).getbuffer()))
    print('BufferedIOBase read Type', type(io.BufferedIOBase(s3object['Body']).read()))
    print('BufferedIOBase read -1 Type', type(io.BufferedIOBase(s3object['Body']).read(-1)))
    #print('BufferedIOBase getbuffer Type', type(io.BufferedIOBase(s3object['Body']).getbuffer()))
    encode_string = base64.b64encode(pdf_data).decode('utf-8')
    '''

    #return encode_string

    #---------------------------------------------------------------
    #
    print('pdf_obj OK---------------------Encode Buffer Start')
    print(json.dumps(encode_string))
    print('pdf_obj OK---------------------Encode Buffer End')
    response = {
        "headers": {
            "Content-Type": "application/pdf",
            "Access-Control-Allow-Origin": "*"  # CORS設定
            #"Access-Control-Allow-Origin":  "https://cl-business-history.s3-ap-northeast-1.amazonaws.com"
            
        }
        ,"statusCode": 200,
        #"body": json.dumps(body),
        "body": json.dumps(encode_string),
        #"body": encode_string,
        "isBase64Encoded" : True, 
    }
    return response
'''
print('pdf_obj OK')
response = {
    "headers": {
        #"Content-Type": "application/pdf",
        #"Access-Control-Allow-Origin": "*"  # CORS設定
        #"Access-Control-Allow-Origin":  "https://cl-business-history.s3-website-ap-northeast-1.amazonaws.com" # CORS設定            
        "Access-Control-Allow-Origin":  "https://cl-business-history.s3-ap-northeast-1.amazonaws.com"
        
    }
    ,"statusCode": 200,
    "body": json.dumps(body),
    #"body": encode_string,
    #"isBase64Encoded" : True, 
}
return response
'''
