#
# Utility
#
import os
from datetime import datetime
from decimal import Decimal
import common_const
import common_log


def get_env() -> dict:
    '''
    環境情報取得

    Parameters
    ----------------------------------------------

    Returns
    ----------------------------------------------
    環境情報 : dict

    '''
    keys = [
        common_const.ENV_ACCESS_CONTROL_ALLOW_ORIGIN
        ,common_const.ENV_M_USER
        ,common_const.DYNAMODB_ENDPOINT
        ,common_const.ENV_T_WORK_HISTORY
    ]
    param_dict = {}
    for key in keys:
        param_dict[key] = os.getenv(key)
        if not param_dict[key] :
            common_log.output(common_log.LOG_WARNING,'Key:{0} Nothing'.format(key),'get_env')
        else:
            common_log.output(common_log.LOG_WARNING,'Key:{0} value:{1}'.format(key,param_dict[key]),'get_env')
    return param_dict


def get_datetime():
    '''
    現在日時(YYYY/MM/DD HH:MM:SS)文字取得関数
    '''
    return datetime.now().strftime("%Y/%m/%d %H:%M:%S")


def jsondumps_custom_proc(obj):
    '''
    JSON変換時のカスタム関数

    Decimal -> float(obj)

    '''
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError
