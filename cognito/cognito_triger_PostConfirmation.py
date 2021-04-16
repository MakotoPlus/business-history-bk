import json,os,boto3

#TABLE_NAME = 'm_user';
ENV_M_USER = 'TABLE_M_USER'

def add_user(userinfo) -> None:
    '''
    Parameter
    ----------------------------------
    userinfo

    '''
    print('add_user start!!')
    #dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
    dynamodb = boto3.resource('dynamodb')
    print('{0}={1}'.format(ENV_M_USER, os.environ[ENV_M_USER]))
    table = dynamodb.Table(os.environ[ENV_M_USER])
    full_name = '{0} {1}'.format(userinfo['family_name'], userinfo['given_name'])
    response = table.put_item(
        Item ={
            'uuid' : userinfo['sub']
            ,'authority' : '0'
            ,'compnaycd' : userinfo['custom:companycd']
            ,'full_name' : full_name
            ,'family_name' : userinfo['family_name']
            ,'given_name' : userinfo['given_name']
            ,'email' : userinfo['email']
        }
    )
    print('dynamo put_item ok!!')
    #print(response);

def run(event, context):
    try:
        print(event);
        print(context);
        add_user(event['request']['userAttributes'])
        return event;
    except:
        import traceback
        traceback.print_exc()
        return {}

if __name__ == '__main__':
    data = {
        'userinfo' : {
            'uuid' : '0001'
            ,'family_name' : 'Fukuda'
            ,'given_name' : 'Makoto'
            ,'email' : 'Fukudapee@test.jp'
        }
    }
    add_user(data)
    print('end')
