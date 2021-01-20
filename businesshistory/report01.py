import json, math, io
from dateutil.relativedelta import relativedelta
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4, portrait
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import mm
from reportlab.lib.units import cm
from reportlab.lib import colors
from datetime import datetime as dt
from monthdelta import monthmod
import pandas as pd

#色を指定するため
from reportlab.lib.colors import red

key_out_name_type = 'out_name_type'
key_output_date = 'output_date'
key_company = 'company'
key_company_address = 'company_address'
key_company_tel = 'company_tel'
key_company_fax = 'company_fax'
key_company_url = 'company_url'
key_usrname = 'usrname'
key_usrname_kana = 'usrname_kana'
key_username_initial = 'username_initial'
key_birthday = 'birthday'
key_gender = 'gender'
key_address = 'address'
key_train = 'train'
key_station = 'station'
key_educational_background = 'educational_background'
key_qualification = 'qualification'
key_pr = 'pr'

key_start_date = 'start_date'
key_end_date = 'end_date'
key_history = 'history'
key_process = 'process'
key_technology = 'technology'
key_language = 'language'
key_fw ='fw'
key_db = 'db'
key_os = 'os'
#工程のKEY情報
key_rd ="RD"
key_bd ="BD"
key_ps ="PS"
key_pg ="PG"
key_ut ="UT"
key_it ="IT"
key_st ="ST"
key_ot ="OT"
key_om ="OM"

key_his_no = 'no'
key_hist_start_date ='start_date'
key_hist_end_date ='end_date'
key_hist_industry ='industry'
key_hist_system ='system'
key_hist_scale ='scale'
key_hist_position ='position'
key_hist_number_pepole ='number_pepole'
key_hist_detail ='detail'
key_hist_start_month = 'start_month'
key_hist_end_month = 'end_month'
key_hist_job_yearmonth = 'job_year_month' #就業期間(X年Xヶ月)
key_hist_jobmonth = 'job_hist_month' #就業期間（月)

'''
業務経歴書出力


データ構造

業務報告書出力するための、JSon型データ定義
{
    req : {
        "out_name_type : "0",
        "output_date": "2020/10/01"
    }
    data : {
        "out_name_type="0"
        "output_date": "2020/10/01",
        "company": "企業名",
        "company_address": "企業住所",
        "company_tel": "企業電話番号",
        "company_fax": "企業FAX番号",
        "company_url": "企業URL",
        "usrname": "名前",
        "usrname_kana": "カナ",
        "username_initial = "M.F"
        "birthday": "yyyy/mm/dd",
        "gender": "男",
        # 業務内容から算出
        # "years_experience": "88年12ヶ月",
        #
        "train": "京浜東北",
        "station": "蕨",
        "address": "埼玉",
        "educational_background": "中卒",
        "qualification": "SAA",
        "pr": "エクボ",
        "history": [
            {
                "no": 1,
                "start_date": "yyyy/mm/dd",
                "end_date": "yyyy/mm/dd",
                "industry": "金融",
                "system": "AWSシステム",
                "scale": "100人月",
                "position": "M",
                "number_pepole": "10",
                "detail": "基本設計とぉー\n詳細",
                "process": [
                    "RD",
                    "BD",
                    "PS",
                    "PG",
                    "UT",
                    "IT",
                    "ST",
                    "OT",
                    "OM"
                ],
                "technology": 
                    {
                        "db" : {
                            "Oracle":"11g"
                            ,"SQLite":"2.0"
                        }
                        ,"os" : {
                            "Windows": "10"
                        }
                    }        },
            {
                "no": 2,
                "start_date": "yyyy/mm/dd",
                "end_date": "yyyy/mm/dd",
                "industry": "金融",
                "system": "AWSシステム",
                "scale": "100人月",
                "position": "M",
                "number_pepole": "10",
                "detail": "基本設計とぉー\n詳細",
                "process": [
                    "RD",
                    "BD",
                    "PS",
                    "PG",
                    "UT",
                    "IT",
                    "ST",
                    "OT",
                    "OM"
                ],
                "technology": 
                    {
                        "language" : {
                            "java":"80"
                            ,"C#":""
                        }
                        ,"fw" : {
                            "Struts":"2.0"
                        }
                        ,"db" : {
                            "Oracle":"11g"
                            ,"SQLite":"2.0"
                        }
                        ,"os" : {
                            "Windows": "10"
                        }
                    }
            }
        ]
    }
}

'''


FONT_NAME = 'HeiseiKakuGo-W5'


class BusinessHistoryReport:
    '''
    業務経歴書出力親クラス


    '''
    def __init__(self, out_filename):
        '''
        コンストラクタ

        paramters
        -----------------------------------
        out_filename:str
            出力PDFファイル名
        Returns
        -----------------------------------
        '''
        self.pdfFile = canvas.Canvas(out_filename)


    def output(self, all_dict_data):
        '''
        業務経歴書出力

        paramters
        -----------------------------------
        dict_data :dict
            出力するDICTデータ

        Returns
        -----------------------------------
        None
        '''
        dict_data = all_dict_data['data']
        dict_req = all_dict_data['req']
        #
        #hisotryのデータ件数より出力ページ数を割出す
        #5件で1ページ
        list_history = dict_data['history']
        print('list_history cnt=', len(list_history))
        if len(list_history) <= 0 :
            print('No data')
            return

        #TEST
        #page = BusinessHistoryFastPage(self)
        #page._sumary(dict_data)
        # 切上げ割算
        page_output = math.ceil(len(list_history) / 5 )
        for page_index in range(page_output):
            if page_index > 0:
                self.pdfFile.showPage()
            #出力するhistoryデータを抽出
            history_data = list_history[page_index * 5 : (page_index * 5 ) + 5]
            #history_dataが 5個満たない場合は空を設定する
            #if len(history_data) < 5:
            for i in range(5-len(history_data)):
                add_dict = {
                    key_his_no: ''
                    ,key_hist_start_date:''
                    ,key_hist_end_date:''
                    ,key_hist_industry:''
                    ,key_hist_system:''
                    ,key_hist_scale:''
                    ,key_hist_position:''
                    ,key_hist_number_pepole:''
                    ,key_hist_detail:''
                    ,key_hist_start_month:''
                    ,key_hist_end_month:''
                    ,key_hist_job_yearmonth:''
                    ,key_hist_jobmonth:''
                }
                history_data.append(add_dict)        
            self.pdfFile.saveState() 
            page = BusinessHistoryFastPage(self)
            self.pdfFile.restoreState()
            page.output_page(page_index+1,page_output, dict_req, dict_data, history_data)
        self.pdfFile.save()


class BusinessHistoryFastPage:
    def __init__(self, owner):
        self.owner = owner
        self.pdfFile = owner.pdfFile
        self.pdfFile.setAuthor('python-izm.com')
        self.pdfFile.setTitle('PDF生成')
        self.pdfFile.setSubject('サンプル')
        # A4
        self.pdfFile.setPageSize((21.0*cm, 29.7*cm))
        # B5
        # pdfFile.setPageSize((18.2*cm, 25.7*cm))
        pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))

    def output_page(self, page, page_max, dict_req, dict_data, history_data):
        '''
        putput_page
        １ページ出力

        Paramaters
        ---------------------------------------
        page : int
            現在のページ番号
        page_max : int
            最大ページ数
        dict_req : dict
            出力条件パラメータ
        dict_data : dict
            出力対象全データ
        history_data : list
            今回ページの出力対象の案件詳細情報(最大5件分)
        '''
        meisai_y = 52
        years_experience = self.__set_sumary(page, 10, 197, dict_data)
        self.__set_header(dict_req, dict_data, years_experience)
        self.__set_meisai_job(page, 10, meisai_y, dict_data, history_data)
        self.__set_meisai_kotei(page, 139, meisai_y, dict_data, history_data)
        self.__set_meisai_env(page, 171, meisai_y, dict_data, history_data)
        self.__set_fotter(page, page_max, 10, 30)

    def __get_age(self, dict_req, dict_data):
        '''
        誕生日と出力年月から年齢を求めて返す

        Paramaters
        ---------------------------------------
        dict_data : dict
            出力対象全データ

        Returns
        ---------------------------------------
        年齢 : int or None
            計算できない場合はNoneを返す
        '''
        try:
            str_birthday = dict_data[key_birthday]
            str_output_date = dict_req[key_output_date]
            birthday = dt.strptime(str_birthday, '%Y/%m/%d')
            outdate = dt.strptime(str_output_date, '%Y/%m/%d')
            dy = relativedelta(outdate, birthday)
            return dy.years
        except Exception as e:
            print( '年齢計算エラー({0})'.format(e))
            return None

    def _get_month(self, str_fromdate, str_todate):
        '''
        稼働開始日、終了日から稼働月数を算出する

        Paramaters
        ---------------------------------------
        str_fromdate : str
            開始日(yyyy/mm/dd)
        str_todate : str
            終了日(yyyy/mm/dd)

        Returns
        ---------------------------------------
        年齢 : int
            計算できない場合は0を返す

        Notes
            業務経歴書は１カ月稼働の場合は
            yyyy/01/01 ～ yyyy/01/31 もしくは yyyy/01/01と入力されているため
            計算結果に + 1 をした値を返す
        ---------------------------------------
        '''
        try:
            from_date = dt.strptime(str_fromdate, '%Y/%m/%d')
            to_date = dt.strptime(str_todate, '%Y/%m/%d')
            mmod = monthmod(from_date, to_date) 
            #print(mmod[0].months) 
            #print( "計算結果=", mmod[0].months+1, type(mmod[0].months))
            return mmod[0].months + 1
        except Exception as e:
            print( '稼働年月計算エラー({0})'.format(e))
            return 0


    def __set_header(self, dict_req, dict_data, years_experience):
        ''' ヘッダー情報設定

        Paramaters
        ---------------------------------------
        dict_req : dict
            出力条件データ
        dict_data : dict
            出力対象全データ
        years_experience : str
            経験年数(NN年NNヶ月)

        '''
        self.pdfFile.setFont(FONT_NAME, 18)
        self.pdfFile.drawString(10*mm, 285*mm, '業務経歴書') 
        self.pdfFile.setFont(FONT_NAME, 8)
        self.pdfFile.drawString(170*mm, 285*mm, dict_req[key_output_date] + ' 現在') 
        self.pdfFile.setFont(FONT_NAME, 9)

        #誕生日と、出力年月(output_date)より年齢を計算する
        age = self.__get_age(dict_req, dict_data)
        age = str(age) if age != None else ''

        #名前は
        # out_name_type = 1 は 通常の名前、名前カナを出力
        # それ以外はイニシャルを名前に出力する
        out_name_type = ''
        username_kana = ''
        username = ''
        if key_out_name_type in dict_req:
            out_name_type = dict_req[key_out_name_type]
        if out_name_type == '1' :
            if key_usrname in dict_data:
                username = dict_data[key_usrname]
            if key_usrname_kana in dict_data:
                username_kana = dict_data[key_usrname_kana]
        else:
            if key_username_initial in dict_data:
                username = dict_data[key_username_initial]


        '''
        data = [
                    ['フリガナ','','生年月日','年齢','性別','経験年数','','最寄駅','現住所'],
                    ['氏名', '','','','','','','',''],
                    ['カマドタンジロウ', '', '1972/10/05','48','男','99年99月', '','京浜東北','東京'],
                    ['釜戸　丹次郎', '','', '','','', '','品川シーサイド',''],
                    ['学\n歴', 'ここに文字改行\n改行したかな','', '','','資\n格','', '',''],
                    ['PR', 'ながいーーーーーー\nーーーーーーーーーーーーーーーー\nーーーーーーーながいーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーいもじ','', '','','','', '',''],
                ]
        '''
        data = [
                    ['フリガナ','','生年月日','年齢','性別','経験年数','','最寄駅','現住所'],
                    ['氏名', '','','','','','','',''],
                    [username_kana, '', dict_data[key_birthday],age,dict_data[key_gender], years_experience, '',dict_data[key_train],dict_data[key_address]],
                    [username, '','', '','','', '',dict_data[key_station],''],
                    ['学\n歴', dict_data[key_educational_background],'', '','','資\n格',dict_data[key_qualification], '',''],
                    ['PR', dict_data[key_pr],'', '','','','', '',''],
                ]
        table = Table(data, colWidths=(8*mm, 45*mm, 25*mm, 10*mm, 10*mm,8*mm, 20*mm, 38*mm, 27*mm), \
            rowHeights=(3*mm,3*mm,5*mm,5*mm,10*mm,15*mm))
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1),FONT_NAME, 9),    
            ('FONT', (0, 2), (1, 2),FONT_NAME, 6),    
            ('FONT', (0, 3), (1, 3),FONT_NAME, 12),    
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
            ('INNERGRID', (0, 0), (8, 2), 1, colors.black),
            ('INNERGRID', (0, 3), (8, 5), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ("VALIGN", (0, 3), (0, 3), "BOTTOM"),            
            ("ALIGN", (3, 2), (4, 3), "CENTER"),            
            ('SPAN', (0, 0), (1, 0)),
            ('SPAN', (2, 0), (2, 1)),
            ('SPAN', (3, 0), (3, 1)),
            ('SPAN', (4, 0), (4, 1)),
            ('SPAN', (5, 0), (6, 1)),
            ('SPAN', (7, 0), (7, 1)),
            ('SPAN', (8, 0), (8, 1)),
            ('SPAN', (0, 1), (1, 1)),
            ('SPAN', (5, 1), (6, 1)),
            ('SPAN', (0, 2), (1, 2)),
            ('SPAN', (0, 3), (1, 3)),
            ('SPAN', (2, 2), (2, 3)),
            ('SPAN', (3, 2), (3, 3)),
            ('SPAN', (4, 2), (4, 3)),
            ('SPAN', (5, 2), (6, 3)),
            ('SPAN', (8, 2), (8, 3)),
            ('SPAN', (0, 3), (1, 3)),
            ('SPAN', (1, 4), (4, 4)),
            ('SPAN', (1, 5), (8, 5)),
            ('SPAN', (6, 4), (8, 4)),
            ('BACKGROUND', (0, 0), (8, 1), colors.lightgrey),            
            ('BACKGROUND', (0, 4), (0, 4), colors.lightgrey),            
            ('BACKGROUND', (0, 5), (0, 5), colors.lightgrey),            
            ('BACKGROUND', (5, 4), (5, 4), colors.lightgrey),            
            ]))

        table.wrapOn(self.pdfFile, 10*mm, 240*mm)
        table.drawOn(self.pdfFile, 10*mm, 240*mm)

    def __set_sumary(self, page, table_x, table_y, dict_data):
        '''
        サマリ―情報の出力

        Parameters
        ----------------------------------------
        page : int
            現在出力ページ番号
        table_x : int
            テーブル出力X位置
        table_y : int
            テーブル出力Y位置
        dict_data : dict
            出力対象全データ

        Return
        ----------------------------------------
        str :
            業務経験年数(99年99月)

        Notes
        ----------------------------------------
        全ての案件情報から技術情報の抽出とトータル期間を算出する
        '''
        years_experience, kotei_values_dict, langs_list, fw_list, db_list, os_list = self.__sumary(dict_data)
        data = [
                    ['工程','年数','', '言語','年数','','F/W','年数','','DB','年数','','OS','年数'],
                    ['要件・調査', kotei_values_dict[key_rd],'',langs_list[0][0],langs_list[0][1],'',fw_list[0][0],fw_list[0][1], '',db_list[0][0],db_list[0][1],'',os_list[0][0],os_list[0][1]],
                    ['基本設計', kotei_values_dict[key_bd],'',langs_list[1][0],langs_list[1][1],'',fw_list[1][0],fw_list[1][1], '',db_list[1][0],db_list[1][1],'',os_list[1][0],os_list[1][1]],
                    ['詳細設計', kotei_values_dict[key_ps],'',langs_list[2][0],langs_list[2][1],'',fw_list[2][0],fw_list[2][1], '',db_list[2][0],db_list[2][1],'',os_list[2][0],os_list[2][1]],
                    ['製造', kotei_values_dict[key_pg],'',langs_list[3][0],langs_list[3][1],'',fw_list[3][0],fw_list[3][1], '',db_list[3][0],db_list[3][1],'',os_list[3][0],os_list[3][1]],
                    ['単体テスト', kotei_values_dict[key_ut],'',langs_list[4][0],langs_list[4][1],'',fw_list[4][0],fw_list[4][1], '',db_list[4][0],db_list[4][1],'',os_list[4][0],os_list[4][1]],
                    ['結合テスト', kotei_values_dict[key_it],'',langs_list[5][0],langs_list[5][1],'',fw_list[5][0],fw_list[5][1], '',db_list[5][0],db_list[5][1],'',os_list[5][0],os_list[5][1]],
                    ['システムテスト', kotei_values_dict[key_st],'',langs_list[6][0],langs_list[6][1],'',fw_list[6][0],fw_list[6][1], '',db_list[6][0],db_list[6][1],'',os_list[6][0],os_list[6][1]],
                    ['運用テスト', kotei_values_dict[key_ot],'',langs_list[7][0],langs_list[7][1],'',fw_list[7][0],fw_list[7][1], '',db_list[7][0],db_list[7][1],'',os_list[7][0],os_list[7][1]],
                    ['運用保守', kotei_values_dict[key_om],'',langs_list[8][0],langs_list[8][1],'',fw_list[8][0],fw_list[8][1], '',db_list[8][0],db_list[8][1],'',os_list[8][0],os_list[8][1]],
                ]
        table = Table(data, colWidths=(24*mm, 10*mm, 3*mm, 24*mm, 10*mm, 3*mm,24*mm, 10*mm, 3*mm,24*mm, 10*mm, 3*mm,24*mm, 10*mm), \
            rowHeights=(4*mm,4*mm,4*mm,4*mm,4*mm,4*mm,4*mm,4*mm,4*mm,4*mm,))
            #rowHeights=(3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,))
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1),FONT_NAME, 6),    
            ('BOX', (0, 0), (1, 9), 1, colors.black),
            ("ALIGN", (1, 1), (1, 9), "RIGHT"),            
            ("ALIGN", (4, 1), (4, 9), "RIGHT"),            
            ("ALIGN", (7, 1), (7, 9), "RIGHT"),            
            ("ALIGN", (10, 1), (10, 9), "RIGHT"),            
            ("ALIGN", (13, 1), (13, 9), "RIGHT"),            
            ('INNERGRID', (0, 0) , (1, 9) , 1, colors.black),
            ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),            
            ('BOX', (3, 0), (4, 9), 1, colors.black),
            ('INNERGRID', (3, 0) , (4, 9) , 1, colors.black),
            ('BACKGROUND', (3, 0), (4, 0), colors.lightgrey),            
            ('BOX', (6, 0), (7, 9), 1, colors.black),
            ('INNERGRID', (6, 0) , (7, 9) , 1, colors.black),
            ('BACKGROUND', (6, 0), (7, 0), colors.lightgrey),            
            ('BOX', (9, 0), (10, 9), 1, colors.black),
            ('INNERGRID', (9, 0) , (10, 9) , 1, colors.black),
            ('BACKGROUND', (9, 0), (10, 0), colors.lightgrey),            
            ('BOX', (12, 0), (13, 9), 1, colors.black),
            ('INNERGRID', (12, 0) , (13, 9) , 1, colors.black),
            ('BACKGROUND', (12, 0), (13, 0), colors.lightgrey),  
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ]))
        table.wrapOn(self.pdfFile, table_x*mm, table_y*mm)
        table.drawOn(self.pdfFile, table_x*mm, table_y*mm)
        return years_experience

    def __set_meisai_job(self, page, table_x, table_y, dict_data, history_data):
        '''
        一覧の案件概要

        parameter
        --------------------------------
        page int 
        '''
        self.pdfFile.setFont(FONT_NAME, 6)
        data = [
                    ['No','期間','','業種','システム','規模','Postion※','人数\n(管理人数)'],
                    [history_data[0][key_his_no],history_data[0][key_hist_start_month],'',history_data[0][key_hist_industry],history_data[0][key_hist_system],history_data[0][key_hist_scale],history_data[0][key_hist_position],history_data[0][key_hist_number_pepole]],
                    ['',history_data[0][key_hist_end_month],'','','','','',''],
                    ['',history_data[0][key_hist_job_yearmonth],'','','','','',''],
                    ['','作\n業\n詳\n細',history_data[0][key_hist_detail],'','','','',''],
                    [history_data[1][key_his_no],history_data[1][key_hist_start_month],'',history_data[1][key_hist_industry],history_data[1][key_hist_system],history_data[1][key_hist_scale],history_data[1][key_hist_position],history_data[1][key_hist_number_pepole]],
                    ['',history_data[1][key_hist_end_month],'','','','','',''],
                    ['',history_data[1][key_hist_job_yearmonth],'','','','','',''],
                    ['','作\n業\n詳\n細',history_data[1][key_hist_detail],'','','','',''],
                    [history_data[2][key_his_no],history_data[2][key_hist_start_month],'',history_data[2][key_hist_industry],history_data[2][key_hist_system],history_data[2][key_hist_scale],history_data[2][key_hist_position],history_data[2][key_hist_number_pepole]],
                    ['',history_data[2][key_hist_end_month],'','','','','',''],
                    ['',history_data[2][key_hist_job_yearmonth],'','','','','',''],
                    ['','作\n業\n詳\n細',history_data[2][key_hist_detail],'','','','',''],
                    [history_data[3][key_his_no],history_data[3][key_hist_start_month],'',history_data[3][key_hist_industry],history_data[3][key_hist_system],history_data[3][key_hist_scale],history_data[3][key_hist_position],history_data[3][key_hist_number_pepole]],
                    ['',history_data[3][key_hist_end_month],'','','','','',''],
                    ['',history_data[3][key_hist_job_yearmonth],'','','','','',''],
                    ['','作\n業\n詳\n細',history_data[3][key_hist_detail],'','','','',''],
                    [history_data[4][key_his_no],history_data[4][key_hist_start_month],'',history_data[4][key_hist_industry],history_data[4][key_hist_system],history_data[4][key_hist_scale],history_data[4][key_hist_position],history_data[4][key_hist_number_pepole]],
                    ['',history_data[4][key_hist_end_month],'','','','','',''],
                    ['',history_data[4][key_hist_job_yearmonth],'','','','','',''],
                    ['','作\n業\n詳\n細',history_data[4][key_hist_detail],'','','','',''],
                    ['','','','','','','',''],
                ]
        table = Table(data, colWidths=(7*mm, 6*mm, 13*mm, 16*mm,39*mm, 14*mm, 17*mm, 17*mm), \
            rowHeights=(
                6*mm,4*mm,4*mm,4*mm,15*mm
                ,4*mm,4*mm,4*mm,15*mm
                ,4*mm,4*mm,4*mm,15*mm
                ,4*mm,4*mm,4*mm,15*mm
                ,4*mm,4*mm,4*mm,15*mm
                ,0*mm # dummy
            )
        )
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1),FONT_NAME, 6),    
            ('BOX', (0, 0), (7, 21), 1, colors.black),
            ('INNERGRID', (0, 0) , (7, 21) , 1, colors.black),
            ('BACKGROUND', (0, 0), (7, 0), colors.lightgrey),
            ("LINEBEFORE", (0, 0), (0, 20), 2, colors.black),
            ("LINEABOVE", (0, 21), (7, 21), 2, colors.black),

            ("LINEABOVE", (0, 0), (7, 0), 2, colors.black),
            ('SPAN', (1, 0), (2, 0)),
            ('SPAN', (0, 1), (0, 4)),
            ('SPAN', (1, 1), (2, 1)),
            ('SPAN', (1, 2), (2, 2)),
            ('SPAN', (1, 3), (2, 3)),
            ('SPAN', (2, 4), (7, 4)),
            ('SPAN', (3, 1), (3, 3)),
            ('SPAN', (4, 1), (4, 3)),
            ('SPAN', (5, 1), (5, 3)),
            ('SPAN', (6, 1), (6, 3)),
            ('SPAN', (7, 1), (7, 3)),
            ('BACKGROUND', (1, 4), (1, 4), colors.lightgrey),
            ("VALIGN", (0, 1), (0, 4), "MIDDLE"),
            ("VALIGN", (1, 3), (1, 4), "MIDDLE"),
            ("VALIGN", (2, 4), (7, 4), "TOP"),
            ("VALIGN", (3, 1), (7, 3), "MIDDLE"),
            ("ALIGN", (1, 1), (2, 3), "CENTER"),
            ("ALIGN", (6, 1), (6, 1), "CENTER"),
            ("ALIGN", (7, 1), (7, 1), "CENTER"),

            ("LINEABOVE", (0, 5), (7, 5), 2, colors.black),
            ('SPAN', (0, 5), (0, 8)),
            ('SPAN', (1, 5), (2, 5)),
            ('SPAN', (1, 6), (2, 6)),
            ('SPAN', (1, 7), (2, 7)),
            ('SPAN', (2, 8), (7, 8)),
            ('SPAN', (3, 5), (3, 7)),
            ('SPAN', (4, 5), (4, 7)),
            ('SPAN', (5, 5), (5, 7)),
            ('SPAN', (6, 5), (6, 7)),
            ('SPAN', (7, 5), (7, 7)),
            ('BACKGROUND', (1, 8), (1, 8), colors.lightgrey),
            ("VALIGN", (0,5), (0,8), "MIDDLE"),
            ("VALIGN", (1,7), (1,8), "MIDDLE"),
            ("VALIGN", (2,8), (7,8), "TOP"),
            ("VALIGN", (3,5), (7,7), "MIDDLE"),
            ("ALIGN", (1, 5), (2, 7), "CENTER"),
            ("ALIGN", (6, 5), (6, 5), "CENTER"),            
            ("ALIGN", (7, 5), (7, 5), "CENTER"),            

            ("LINEABOVE", (0, 9), (7, 9), 2, colors.black),
            ('SPAN', (0, 9), (0, 12)),
            ('SPAN', (1, 9), (2, 9)),
            ('SPAN', (1, 10), (2, 10)),
            ('SPAN', (1, 11), (2, 11)),
            ('SPAN', (2, 12), (7, 12)),
            ('SPAN', (3, 9), (3, 11)),
            ('SPAN', (4, 9), (4, 11)),
            ('SPAN', (5, 9), (5, 11)),
            ('SPAN', (6, 9), (6, 11)),
            ('SPAN', (7, 9), (7, 11)),
            ('BACKGROUND', (1, 12), (1, 12), colors.lightgrey),
            ("VALIGN", (0,9), (0,12), "MIDDLE"),
            ("VALIGN", (1,11), (1,12), "MIDDLE"),
            ("VALIGN", (2,12), (7,12), "TOP"),
            ("VALIGN", (3,9), (7,11), "MIDDLE"),
            ("ALIGN", (1, 9), (2, 11), "CENTER"),
            ("ALIGN", (6, 9), (6, 9), "CENTER"),            
            ("ALIGN", (7, 9), (7, 9), "CENTER"),            

            ("LINEABOVE", (0, 13), (7, 13), 2, colors.black),
            ('SPAN', (0, 13), (0, 16)),
            ('SPAN', (1, 13), (2, 13)),
            ('SPAN', (1, 14), (2, 14)),
            ('SPAN', (1, 15), (2, 15)),
            ('SPAN', (2, 16), (7, 16)),
            ('SPAN', (2, 17), (7, 17)),
            ('SPAN', (3, 13), (3, 15)),
            ('SPAN', (4, 13), (4, 15)),
            ('SPAN', (5, 13), (5, 15)),
            ('SPAN', (6, 13), (6, 15)),
            ('SPAN', (7, 13), (7, 15)),
            ('BACKGROUND', (1, 16), (1, 16), colors.lightgrey),
            ("VALIGN", (0,13), (0,16), "MIDDLE"),
            ("VALIGN", (1,15), (1,16), "MIDDLE"),
            ("VALIGN", (2,16), (7,16), "TOP"),
            ("VALIGN", (3,13), (7,15), "MIDDLE"),
            ("ALIGN", (1, 13), (2, 15), "CENTER"),
            ("ALIGN", (6, 13), (6, 13), "CENTER"),            
            ("ALIGN", (7, 13), (7, 13), "CENTER"),            

            ("LINEABOVE", (0, 17), (7, 17), 2, colors.black),
            ('SPAN', (0, 17), (0, 20)),
            ('SPAN', (1, 17), (2, 17)),
            ('SPAN', (1, 18), (2, 18)),
            ('SPAN', (1, 19), (2, 19)),
            ('SPAN', (2, 20), (7, 20)),
            ('SPAN', (3, 17), (3, 19)),
            ('SPAN', (4, 17), (4, 19)),
            ('SPAN', (5, 17), (5, 19)),
            ('SPAN', (6, 17), (6, 19)),
            ('SPAN', (7, 17), (7, 19)),
            ('BACKGROUND', (1, 20), (1, 20), colors.lightgrey),
            ("VALIGN", (0,17), (0,20), "MIDDLE"),
            ("VALIGN", (1,19), (1,20), "MIDDLE"),
            ("VALIGN", (2,20), (7,20), "TOP"),
            ("VALIGN", (3,17), (7,19), "MIDDLE"),
            ("ALIGN", (1, 17), (2, 19), "CENTER"),
            ("ALIGN", (6, 17), (6, 17), "CENTER"),            
            ("ALIGN", (7, 17), (7, 17), "CENTER"),            
            ]))
        table.wrapOn(self.pdfFile, table_x*mm, table_y*mm)
        table.drawOn(self.pdfFile, table_x*mm, table_y*mm)

        self.pdfFile.setFont(FONT_NAME, 9)
        self.pdfFile.drawString(10*mm, 47*mm, '※ PM:プロジェクトマネージャ/PL:プロジェクトリーダ/SL:サブリーダ/M:メンバ/AM:アーキテクト') 

    def __set_meisai_kotei(self, page, table_x, table_y,dict_data, history_data):
        '''
        一覧の工程出力

        parameter
        --------------------------------
        page int 
        '''

        kotei_list = self.__get_meisai_kotei_list(history_data)
        print(kotei_list)
        data = [['工程','対象']]
        data.extend(kotei_list)
        data.append(['','']) #dummy
        '''
        data = [
            ['工程','対象'],
            ['要件・調査',kotei_list[0]],
            ['基本設計',kotei_list[1]],
            ['詳細設計',kotei_list[2]],
            ['製造',kotei_list[3]],
            ['単体テスト',kotei_list[4]],
            ['結合テスト',kotei_list[5]],
            ['システムテスト',kotei_list[6]],
            ['運用テスト',kotei_list[7]],
            ['運用保守',kotei_list[8]],

            ['要件・調査',kotei_list[9]],
            ['基本設計',kotei_list[10]],
            ['詳細設計',kotei_list[11]],
            ['製造',kotei_list[12]],
            ['単体テスト',kotei_list[13]],
            ['結合テスト',kotei_list[14]],
            ['システムテスト',kotei_list[15]],
            ['運用テスト',kotei_list[16]],
            ['運用保守',kotei_list[17]],

            ['要件・調査',kotei_list[18]],
            ['基本設計',kotei_list[19]],
            ['詳細設計',kotei_list[20]],
            ['製造',kotei_list[21]],
            ['単体テスト',kotei_list[22]],
            ['結合テスト',kotei_list[23]],
            ['システムテスト',kotei_list[24]],
            ['運用テスト',kotei_list[25]],
            ['運用保守',kotei_list[26]],

            ['要件・調査',kotei_list[27]],
            ['基本設計',kotei_list[28]],
            ['詳細設計',kotei_list[29]],
            ['製造',kotei_list[30]],
            ['単体テスト',kotei_list[31]],
            ['結合テスト',kotei_list[32]],
            ['システムテスト',kotei_list[33]],
            ['運用テスト',kotei_list[34]],
            ['運用保守',kotei_list[35]],

            ['要件・調査',kotei_list[36]],
            ['基本設計',kotei_list[37]],
            ['詳細設計',kotei_list[38]],
            ['製造',kotei_list[39]],
            ['単体テスト',kotei_list[40]],
            ['結合テスト',kotei_list[41]],
            ['システムテスト',kotei_list[42]],
            ['運用テスト',kotei_list[43]],
            ['運用保守',kotei_list[44]],
            ['',''], #dummy
        ]
        '''
        table = Table(data, colWidths=(24*mm, 8*mm), \
            rowHeights=(
                6*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm
                ,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm
                ,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm
                ,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm
                ,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm
                ,0*mm #dummy
                )
            )
            #rowHeights=(6*mm,4*mm,4*mm,4*mm,4*mm,4*mm,4*mm,4*mm,4*mm,4*mm,))
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1),FONT_NAME, 5),    
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0) , (-1, -1) , 1, colors.black),
            ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),            
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("ALIGN", (1, 0), (1, 46), "CENTER"),
            ("LINEABOVE", (0, 0), (1, 0), 2, colors.black),
            ("LINEABOVE", (0, 10), (1, 10), 2, colors.black),
            ("LINEABOVE", (0, 19), (1, 19), 2, colors.black),
            ("LINEABOVE", (0, 28), (1, 28), 2, colors.black),
            ("LINEABOVE", (0, 37), (1, 37), 2, colors.black),
            ("LINEABOVE", (0, 46), (1, 46), 2, colors.black),
            ]))
        table.wrapOn(self.pdfFile, table_x*mm, table_y*mm)
        table.drawOn(self.pdfFile, table_x*mm, table_y*mm)

    def __set_meisai_env(self, page,table_x, table_y, dict_data, history_data):
        '''
        一覧の言語環境出力

        parameter
        --------------------------------
        page int 
        '''
        self.pdfFile.setFont(FONT_NAME, 8)
        data = self.__get_meisai_env_list(history_data)
        data.insert(0,['言語/環境','Ver',''])
        data.append(['','','']) #dummy
        '''
        data = [
                    ['言語/環境','Ver',''],
                    ['Java','8.1',''],
                    ['Oracle','11g',''],
                    ['AWS','',''],
                    ['S3','11.0',''],
                    ['','',''],
                    ['','',''],
                    ['','',''],
                    ['','',''],
                    ['','',''],

                    ['Java','8.1',''],
                    ['Oracle','11g',''],
                    ['AWS','',''],
                    ['S3','11.0',''],
                    ['','',''],
                    ['','',''],
                    ['','',''],
                    ['','',''],
                    ['','',''],

                    ['Java','8.1',''],
                    ['Oracle','11g',''],
                    ['AWS','',''],
                    ['S3','11.0',''],
                    ['','',''],
                    ['','',''],
                    ['','',''],
                    ['','',''],
                    ['','',''],

                    ['Java','8.1',''],
                    ['Oracle','11g',''],
                    ['AWS','',''],
                    ['S3','11.0',''],
                    ['','',''],
                    ['','',''],
                    ['','',''],
                    ['','',''],
                    ['','',''],

                    ['Java','8.1',''],
                    ['Oracle','11g',''],
                    ['AWS','',''],
                    ['S3','11.0',''],
                    ['','',''],
                    ['','',''],
                    ['','',''],
                    ['','',''],
                    ['','',''],

                    ['','',''], #dummy
                ]
        '''
        table = Table(data, colWidths=(20*mm, 10*mm, 0*mm), \
            rowHeights=(
                6*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm
                ,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm
                ,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm
                ,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm
                ,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm,3*mm
                ,0*mm #dummy
                )
            )
            #rowHeights=(6*mm,4*mm,4*mm,4*mm,4*mm,4*mm,4*mm,4*mm,4*mm,4*mm,))
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1),FONT_NAME, 5),    
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0) , (-1, -1) , 1, colors.black),
            ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),            
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("ALIGN", (1, 0), (1, 46), "RIGHT"),
            ("LINEABOVE", (0, 0), (1, 0), 2, colors.black),
            ("LINEABOVE", (0, 10), (1, 10), 2, colors.black),
            ("LINEABOVE", (0, 19), (1, 19), 2, colors.black),
            ("LINEABOVE", (0, 28), (1, 28), 2, colors.black),
            ("LINEABOVE", (0, 37), (1, 37), 2, colors.black),
            ("LINEABOVE", (0, 46), (1, 46), 2, colors.black),
            ("LINEBEFORE", (2, 0), (2, 46), 2, colors.black),
            ]))
            #("LINEBEFORE", (0, 0), (0, 46), 2, colors.black),
        table.wrapOn(self.pdfFile, table_x*mm, table_y*mm)
        table.drawOn(self.pdfFile, table_x*mm, table_y*mm)

    def __set_fotter(self, page, maxpage, fotter_x, fotter_y):
        self.pdfFile.setFont(FONT_NAME, 8)
        self.pdfFile.drawString(fotter_x*mm, fotter_y*mm, '株式会社クロスアクティブ') 
        ido = 3
        fotter_y -= ido
        self.pdfFile.setFont(FONT_NAME, 8)
        self.pdfFile.drawString(fotter_x*mm, fotter_y*mm, '〒102-0084 東京都千代田区二番町4番地3 二番町カシュービル5F') 
        fotter_y -= ido
        self.pdfFile.setFont(FONT_NAME, 8)
        self.pdfFile.drawString(fotter_x*mm, fotter_y*mm, 'TEL:03-32633-8030 / FAX:03-3263-8090') 
        fotter_y -= ido
        self.pdfFile.setFont(FONT_NAME, 8)
        self.pdfFile.drawString(fotter_x*mm, fotter_y*mm, 'URL:https://www.xactive.co.jp') 

        fotter_y -= ido
        self.pdfFile.setFont(FONT_NAME, 9)
        self.pdfFile.drawString(190*mm, fotter_y*mm, '{0}/{1}'.format(page, maxpage)) 


    def __sumary(self, dict_data):
        '''
        サマリ情報を返す

        Parameters
        ----------------------------------------
        dict_data : dict
            出力対象全データ

        Returns
        ----------------------------------------
        years_experience : str
            経験年数(yy年mmヶ月)
        kotei_values_dict : dict
            工程をキーに、経験年数を格納, 該当工程がないものは空白を設定
        langs_list : list in ["name", 経験年数]
            経験した言語と年数を格納した文字列配列が格納されたリストを返す。
            リストの順序は年数の降順で設定
            存在しない場合は、空の文字が設定されたリストを返す。
            最低でも9のリストを返す
        fw_list : list in ["name", 経験年数]
            経験したFWと年数を格納した文字列配列が格納されたリストを返す。
            リストの順序は年数の降順で設定
            存在しない場合は、空の文字が設定されたリストを返す。
            最低でも9のリストを返す
        db_list : list in ["name", 経験年数]
            経験したDBと年数を格納した文字列配列が格納されたリストを返す。
            リストの順序は年数の降順で設定
            存在しない場合は、空の文字が設定されたリストを返す。
            最低でも9のリストを返す
        os_list : list in ["name", 経験年数]
            経験したOSと年数を格納した文字列配列が格納されたリストを返す。
            リストの順序は年数の降順で設定
            存在しない場合は、空の文字が設定されたリストを返す。
            最低でも9のリストを返す
        '''
        print('sumary--start')
        #
        # 1. 全ての業務報告書の期間を算出する。
        #s_target = json.dumps(dict_data[key_history])
        experience = 0
        for dict_history in dict_data[key_history]:
            #print('from:{0} to:{1}'.format(dict_history[key_start_date], dict_history[key_end_date]))
            # 就業期間算出 (月)
            job_month = self._get_month(dict_history[key_start_date],dict_history[key_end_date])
            experience += job_month
            # 就業期間をdictへ格納する
            dict_history[key_hist_jobmonth] = job_month
            # 就業期間 N年Nヶ月をdictへ格納する
            job_year = math.floor(job_month/12)
            dict_history[key_hist_job_yearmonth] = \
                '{0:02}年{1:02}ヶ月'.format(job_year
                , job_month - (job_year*12))
            #就業開始年月
            from_date = dt.strptime(dict_history[key_start_date], '%Y/%m/%d')            
            dict_history[key_hist_start_month] = from_date.strftime('%Y{0}%m{1}').format(*'年月')

            #就業終了年月
            to_date = dt.strptime(dict_history[key_end_date], '%Y/%m/%d')
            dict_history[key_hist_end_month] = to_date.strftime('%Y{0}%m{1}').format(*'年月')

        #経験年数設定
        job_year = math.floor(experience/12)
        years_experience = \
            '{0:02}年{1:02}ヶ月'.format(job_year
            , experience - (job_year*12))
        #for dict_history in dict_data['history']:
        #    print('job_month', dict_history['job_month'])

        # 2. 工程、言語、FW,DB,OSの情報の集計&ソートを実施する。
        # 言語は、下記のような構成で降順に設定される
        #  [ {'Java', 10.0},{'COBOL',9.5}]
        kotei_values_dict = self.__summary_kotei(dict_data)
        print(dict_data)
        langs_list = self.__tecnorogy_sumary(dict_data, key_language, 9)
        print(langs_list)
        fw_list = self.__tecnorogy_sumary(dict_data, key_fw, 9)
        print(fw_list)
        db_list = self.__tecnorogy_sumary(dict_data, key_db, 9)
        print(db_list)
        os_list = self.__tecnorogy_sumary(dict_data, key_os, 9)
        print(os_list)
        #df_s = pd.read_json(s_target)
        #print(df_s)
        #print('sumary--end')

        return years_experience, kotei_values_dict, langs_list, fw_list, db_list, os_list

    def __summary_kotei(self, dict_data) -> dict:
        '''
        工程の集計

        Returns
        -------------------------------
        dict 
            工程ごとの合計値
        '''
        # 1.工程用のpandasデータ生成するためにDICTを生成
        #
        #   工程のリストと同じ順序で該当の就業月のリストのDICTを生成する
        #   dict = { 'kotei': ['ST', 'IT', 'PG']
        #           'value': [ 10, 8, 9 ] }
        kotei_list = {}
        item_list = []
        item_value = []
        for dict_history in dict_data[key_history]:
            for process_item in dict_history[key_process]:
                #print( 'item={0} value={1}'.format(process_item, dict_history[key_hist_jobmonth]))
                # 工程と、就業月をリストに追加
                item_list.append(process_item)
                item_value.append(dict_history[key_hist_jobmonth])

        #dictを生成
        kotei_list['kotei'] = item_list
        kotei_list['value'] = item_value
        print( '----------------------------------------')
        print(kotei_list)
        # 2.pandasデータ生成
        print( '----------------------------------------')
        pd_kotei = pd.read_json(json.dumps(kotei_list))
        print(pd_kotei)
        print( '----------------------------------------')     

        #print(pd_kotei.describe())
        #print(pd_kotei.groupby(['kotei'])['value'].sum())


        #集計
        # 工程単位で就業月をサマリしたdictを生成する
        kotei_values = pd_kotei.groupby(['kotei'])['value'].sum()
        kotei_values_dict = kotei_values.to_dict()

        # 工程がKeyに存在しない場合は空データを作成しておく
        if key_rd in kotei_values_dict:
            kotei_values_dict[key_rd] = round(kotei_values_dict[key_rd]/12,2)
        else:
            kotei_values_dict[key_rd] = ''
        if key_bd in kotei_values_dict :
            kotei_values_dict[key_bd] = round(kotei_values_dict[key_bd] /12,2)
        else:
            kotei_values_dict[key_bd] = ''
        if key_ps in kotei_values_dict :
            kotei_values_dict[key_ps] = round(kotei_values_dict[key_ps]/12,2)
        else:            
            kotei_values_dict[key_ps] = ''
        if key_pg in kotei_values_dict :
            kotei_values_dict[key_pg] = round(kotei_values_dict[key_pg]/12,2)
        else:            
            kotei_values_dict[key_pg] = ''
        if key_ut in kotei_values_dict :
            kotei_values_dict[key_ut] = round(kotei_values_dict[key_ut] /12,2)
        else:            
            kotei_values_dict[key_ut] = ''
        if key_it in kotei_values_dict :
            kotei_values_dict[key_it] = round(kotei_values_dict[key_it]/12,2)
        else:            
            kotei_values_dict[key_it] = ''
        if key_st in kotei_values_dict :
            kotei_values_dict[key_st] = round(kotei_values_dict[key_st]/12,2)
        else:            
            kotei_values_dict[key_st] = ''
        if key_ot in kotei_values_dict :
            kotei_values_dict[key_ot] = round(kotei_values_dict[key_ot]/12,2)
        else:            
            kotei_values_dict[key_ot] = ''
        if key_om in kotei_values_dict :
            kotei_values_dict[key_om] = round(kotei_values_dict[key_om]/12,2)
        else:            
            kotei_values_dict[key_om] = ''
        
        return kotei_values_dict

    '''
    def __summary_lang(self, dict_data):
        言語の集計

        Returns
        -------------------------------
        list 
            言語ごとの合計値
        # 1.言語用のpandasデータ生成するためにDICTを生成
        #
        #   工程のリストと同じ順序で該当の就業月のリストのDICTを生成する
        #   dict = { 'lang': ['Java', 'Python', 'COBOL']
        #           'value': [ 10, 8, 9 ] }
        lang_list  =[]
        lang_value  =[]
        for dict_history in dict_data[key_history]:
            dict_language = []
            if key_technology in dict_history :
                if key_language in dict_history[key_technology]:
                    dict_language = dict_history[key_technology][key_language]
            print(dict_language)
            lang_list.extend(dict_language.keys())            
            lang_value.extend([dict_history[key_hist_jobmonth]] * len(dict_language))
        #dictを生成
        print( '----------------------------------------')
        # 2.pandasデータ生成
        print( '----------------------------------------')
        langs_list = {}
        langs_list['lang'] = lang_list
        langs_list['value'] = lang_value
        pd_langs = pd.read_json(json.dumps(langs_list))
        print(pd_langs)
        print( 'Lang　集計----------------------------------------')
        #print( '----------------------------------------')
        #集計
        print(pd_langs.groupby(['lang'])['value'].sum())
        pd_langs_sum = pd_langs.groupby(['lang'])['value'].sum()
        #
        #集計結果を値の降順にソート
        pd_langs_sorted = pd_langs_sum.sort_values(ascending=False)
        print( 'Lang　降順にソート----------------------------------------')
        print(pd_langs_sum.sort_values(ascending=False))
        #list化
        print( 'Lang　List化----------------------------------------')
        langs_list = pd_langs_sorted.reset_index().values.tolist()

        #list内の期間を月から年に変更する
        for lang in langs_list:
            lang[1] = round(lang[1]/12,2)
        print(langs_list)
        return langs_list
    '''
    def __tecnorogy_sumary(self, dict_data, tecnorogy_param, min) -> list:
        '''
        TECNOROGYの集計共通(language, fw, db, os)

        Parameters
        -------------------------------
        tecnorogy_key : str
            language,fw,db,os

        Returns
        -------------------------------
        list in [name(str), value(int)] 
            
        '''

        debug_print = False
        if debug_print:
            print( 'start __tecnorogy_sumary parameter={0}'.format(tecnorogy_param))

        # 1.言語用のpandasデータ生成するためにDICTを生成
        #
        #   工程のリストと同じ順序で該当の就業月のリストのDICTを生成する
        #   dict = { 'lang': ['Java', 'Python', 'COBOL']
        #           'value': [ 10, 8, 9 ] }
        tec_list  =[]
        tec_value  =[]
        for dict_history in dict_data[key_history]:
            dict_technology = []
            if key_technology in dict_history :
                if tecnorogy_param in dict_history[key_technology]:
                    dict_technology = dict_history[key_technology][tecnorogy_param]
            if debug_print:
                print(dict_technology)
            if len(dict_technology) > 0:
                tec_list.extend(dict_technology.keys())            
                tec_value.extend([dict_history[key_hist_jobmonth]] * len(dict_technology))
        #dictを生成
        if debug_print:
            print( '----------------------------------------')
        # 2.pandasデータ生成
        technology_list = {}
        technology_list['key'] = tec_list
        technology_list['value'] = tec_value
        pd_technology = pd.read_json(json.dumps(technology_list))
        if debug_print:
            print(pd_technology)
        #集計
        if debug_print:
            print( 'pd_technology　集計----------------------------------------')
            print(pd_technology.groupby(['key'])['value'].sum())
        pd_technology_sum = pd_technology.groupby(['key'])['value'].sum()
        #
        #集計結果を値の降順にソート
        pd_technology_sorted = pd_technology_sum.sort_values(ascending=False)
        if debug_print:
            print( 'pd_technology　降順にソート----------------------------------------')
            print(pd_technology_sum.sort_values(ascending=False))
        #list化
        if debug_print:
            print( 'pd_technology　List化----------------------------------------')
        technology_list = pd_technology_sorted.reset_index().values.tolist()

        #list内の期間を月から年に変更する
        for tec in technology_list:
            tec[1] = round(tec[1]/12,2)
        #結果が最低数を満たない場合は空を設定する
        #if len(technology_list) < min:
        for i in range(min - len(technology_list)):
            technology_list.append(["",""])
        if debug_print:
            print(technology_list)
            print( 'end __tecnorogy_sumary parameter={0}'.format(tecnorogy_param))
        return technology_list        

    def __get_meisai_kotei_list(self, history_data) ->list:
        '''
        明細項目の工程の出力値のリストを返す。

        RD,BD,PS,PG,UT,IT,ST,OT,OMの順で〇を設定する
        '''
        ret_list = []
        keys = [
            key_rd
            ,key_bd
            ,key_ps
            ,key_pg
            ,key_ut
            ,key_it
            ,key_st
            ,key_ot
            ,key_om
        ]
        labels = [
            '要件・調査'
            ,'基本設計'
            ,'詳細設計'
            ,'製造'
            ,'単体テスト'
            ,'結合テスト'
            ,'システムテスト'
            ,'運用テスト'
            ,'運用保守'
        ]

        for his in history_data:
            if False == (key_process in his):
                for label in labels:
                    ret_list.append([label,''])
                continue
            for i in range(len(keys)):
                if keys[i] in his[key_process]:
                    ret_list.append([labels[i], '○'])
                else:
                    ret_list.append([labels[i],''])
        return ret_list

    def __get_meisai_env_list(self, history_data) ->list:
        ret_list = []
        for his in history_data:
            if False == (key_technology in his):
                for i in range(9):
                    ret_list.append(['','',''])
                continue
            add_list = []
            if key_language in his[key_technology]:
                for key in his[key_technology][key_language].keys():
                    add_list.append([key, his[key_technology][key_language][key],''])
            if key_fw in his[key_technology]:
                for key in his[key_technology][key_fw].keys():
                    add_list.append([key, his[key_technology][key_fw][key],''])
            if key_db in his[key_technology]:
                for key in his[key_technology][key_db].keys():
                    add_list.append([key, his[key_technology][key_db][key],''])
            if key_os in his[key_technology]:
                for key in his[key_technology][key_os].keys():
                    add_list.append([key, his[key_technology][key_os][key],''])
            #
            # リストの数を9に調整する
            add_list = add_list[:9]
            for i in range(9 - len(add_list)):
                add_list.append(['','',''])
            #
            # めんどいけどループして追加 extendでは、配列が全て展開されちゃうため
            for add in add_list:
                ret_list.append(add)
        return ret_list


if __name__ == '__main__':
    print('start')

    FILENAME="./testdata001.json"
    
    with open(FILENAME, mode='r', encoding="utf_8") as fd:
        data = json.load(fd)
    print("date : ", data)
    print( type(data))

    bytes_buffer = io.BytesIO()
    ##pdf = BusinessHistoryReport('./0051_history.pdf')
    pdf = BusinessHistoryReport(bytes_buffer)
    pdf.output(data)
    with open('./output.pdf', mode='wb') as fd:
        fd.write(bytes_buffer.getbuffer())
    #print(bytes_buffer)
    print('end')

