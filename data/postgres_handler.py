
# Author  : 이병헌
# Contact : lww7438@gmail.com
# Date    : 2022-10-21(금)



# Required Modules
import psycopg2    # Command to install: "pip install psycopg2-binary"

import conn_config      as config
import api_handler      as api
import data_manipulator as dm



# Configurations
TYPE_basic_stock_info = {
    'isin_code'       : 'varchar',
    'short_isin_code' : 'varchar',
    'market_category' : 'varchar',
    'item_name'       : 'varchar',
    'corp_name'       : 'varchar',
    'corp_number'     : 'varchar',
    'listing_date'    : 'date',
    'issue_cnt'       : 'bigint',
    'industry'        : 'varchar',
    'face_value'      : 'integer',
}

TYPE_financial_info = {
    'isin_code' : 'varchar',
    'bps'       : 'integer',
    'per'       : 'double precision',
    'pbr'       : 'double precision',
    'eps'       : 'integer',
    'div'       : 'double precision',
    'dps'       : 'integer',
}

TYPE_member_info = {
    'member_id'    : 'varchar',
    'member_pw'    : 'varchar',
    'member_email' : 'varchar',
}

TYPE_news_info = {
    'isin_code'  : 'varchar',
    'write_date' : 'date',
    'headline'   : 'varchar',
    'sentiment'  : 'double precision',
    'news_id'    : 'bigint', # Serial8 Type
}

TYPE_price_info = {
    'base_date'        : 'date',
    'isin_code'        : 'varchar',
    'market_price'     : 'integer',
    'close_price'      : 'integer',
    'high_price'       : 'integer',
    'low_price'        : 'integer',
    'fluctuation'      : 'integer',
    'fluctuation_rate' : 'double precision',
    'volume'           : 'bigint',
}

TYPE_world_index_info = {

}

TYPE_world_index_price = {
    
}

LIST_TABLE_NAME = [
    'basic_stock_info',
    'member_info',
    'price_info',
    'news_info',
    'financial_info'
]

SCHEMA = {
    'basic_stock_info' : TYPE_basic_stock_info,
    'member_info'      : TYPE_member_info,
    'price_info'       : TYPE_price_info,
    'news_info'        : TYPE_news_info,
    'financial_info'   : TYPE_financial_info,
}

STR_TYPES  = ['varchar', 'text', 'char', 'date']
NULL_TYPES = [None, 'None', 'none', 'NULL', 'null', 'nullptr', '']



# Functions
def get_type_by_column_name(table:str=None, column:str=None):
    
    try:
        return SCHEMA[table][column]

    except Exception as err_msg:
        print(f"[ERROR] Schema Error: {err_msg}")


# Class Declaration
class PostgresHandler():

    # * * *    Low-Level Methods (SQL Handlers)    * * *
    def __init__(self, user:str, password:str, host=config.POSTGRES_HOST, port=config.POSTGRES_PORT, db_name=config.PORTGRES_DB_NAME):

        self._client = psycopg2.connect(
            host     = host,
            port     = port,
            dbname   = db_name,
            user     = user,
            password = password            
        )

        self.conn_user = user
        self.cursor = self._client.cursor()

    def __del__(self):

        self._client.close()
        self.cursor.close()

    def __execute(self, query:str, args={}):

        self.cursor.execute(query,args)
        row = self.cursor.fetchall()
        return row

    def __commit(self):

        self.cursor.commit()

    def insert_item(self, schema:str='postgres', table:str=None, columns:list=None, data:dict=None):

        if (table not in LIST_TABLE_NAME) or (table is None):
            raise f"[ERROR] Invalid Table Name: {table} does not exist"

        if data is None:
            raise f"[ERROR] Empty Data Insertion: data is empty"

        values = ""

        for column in columns:
            
            if data[column] in NULL_TYPES:
                values += "None" + ", "
            elif get_type_by_column_name(table, column) in STR_TYPES:
                values += "'" + str(data[column]) + "', "
            else:
                values += str(data[column]) + ", "

        values = values[:-2]

        sql = f""" INSERT INTO {table} ({', '.join(columns)}) VALUES ({values}) ;"""

        print("SQL: ", sql)

        try:
            self.cursor.execute(sql)
            self._client.commit()

        except Exception as err_msg :
            print(f"[ERROR] Insert Error: {err_msg}") 

    def insert_items(self, table:str=None, columns:list=None, data:list=None):

        if (table not in LIST_TABLE_NAME) or (table is None):
            raise f"[ERROR] Invalid Table Name: {table} does not exist"

        if data is None:
            raise f"[ERROR] Empty Data Insertion: data is empty"

        value_list = []
        
        for row in data:
            values = "("
            for column in columns:

                if row[column] in NULL_TYPES:
                    values += "null" + ", "
                elif get_type_by_column_name(table, column) in STR_TYPES:
                    values += "'" + str(row[column]) + "', "
                else:
                    values += str(row[column]) + ", "
                    
            values = values[:-2]
            values += ")"
            value_list.append(values)

        sql = f""" INSERT INTO {table} ({', '.join(columns)}) VALUES """
        for value in value_list:
            sql += value + ', '

        sql = sql[:-2]
        sql += ';'

        print("SQL: ", sql)

        try:
            self.cursor.execute(sql)
            self._client.commit()

        except Exception as err_msg :
            print(f"[ERROR] Insert Error: {err_msg}") 
    
    def find_item(self, table:str=None, columns='ALL', condition:str=None):

        if (table not in LIST_TABLE_NAME) or (table is None):
            raise f"[ERROR] Invalid Table Name: {table} does not exist"

        if columns == 'ALL':
            columns = "*"
        elif type(list()) == type(columns):
            columns = ", ".join(columns)
            columns = "(" + columns + ")"
        elif type(str()) == type(columns):
            pass
            
        if condition is None:
            sql = f""" SELECT {columns} FROM {table} ;"""
        else:
            sql = f""" SELECT {columns} FROM {table} WHERE {condition} ;"""

        print("SQL: ", sql)

        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()

        except Exception as err_msg:
            result = (f"[ERROR] Select Error: {err_msg}")
        
        return result

    def update_item(self, table:str=None, column:str=None, value=None, condition:str=None):

        if (table not in LIST_TABLE_NAME) or (table is None):
            raise f"[ERROR] Invalid Table Name: {table} does not exist"

        if get_type_by_column_name(table, column) in STR_TYPES:
            value = "'" + value + "'"
        
        sql = f" UPDATE {table} SET {column}={value} WHERE {condition} ;"

        try :
            self.cursor.execute(sql)
            self._client.commit()

        except Exception as err_msg:
            print(f"[ERROR] Update Error: {err_msg}")

    def delete_item(self, table:str=None, condition:str=None):
        
        if (table not in LIST_TABLE_NAME) or (table is None):
            raise f"[ERROR] Invalid Table Name: {table} does not exist"

        if condition is None:
            sql = f" DELETE FROM {table} ;"
        else:
            sql = f" DELETE FROM {table} WHERE {condition} ;"

        try :
            self.cursor.execute(sql)
            self._client.commit()

        except Exception as err_msg:
            print(f"[ERROR] Delete Error: {err_msg}")

    # * * *    High-Level Methods    * * *
    def build_basic_stock_info(self):
        """
        데이터베이스의 basic_stock_info 테이블에 KOSPI, KOSDAQ, KONEX에 상장된 전 종목에 대한 기본정보들을 저장한다.
        ※ 본 메서드는 DBA만 수행할 수 있다.

        [Parameters]
        -
        
        [Returns]
        -
        """

        # DBA Only can run initial building function
        if(self.conn_user != config.ID_DBA):
            print("Only DBA can run the build function")
            return False

        try:           
            # Clear Table
            self.delete_item(table='basic_stock_info')
            
            # Listing All Stock
            krx_listed_info = api.get_krx_listed_info(serviceKey=config.API_KEY_OPEN_DATA_PORTAL)
            krx_listed_info = dm.filter_params(data_list=krx_listed_info, params=['isinCd', 'mrktCtg', 'itmsNm', 'crno', 'corpNm', 'shotnIsin'])
            basic_stock_info = []

            # Remove Duplicates in krx_listed_info
            for i in range(len(krx_listed_info)):
                if krx_listed_info[i] not in krx_listed_info[i+1:]:
                    basic_stock_info.append(krx_listed_info[i])

            for krx_stock in basic_stock_info:
                item_basi_info = api.get_item_basi_info(serviceKey=config.API_KEY_OPEN_DATA_PORTAL, crno=krx_stock['crno'])

                if item_basi_info is not None:
                    item_basi_info = dm.filter_params(data_list=item_basi_info, params=['isinCd', 'stckParPrc', 'issuStckCnt', 'lstgDt'])
                    
                    for key, value in item_basi_info[0].items():
                        krx_stock[key] = value       

                # Column Renaming
                krx_stock['isin_code'] = krx_stock.pop('isinCd', None)
                krx_stock['market_category'] = krx_stock.pop('mrktCtg', None)
                krx_stock['item_name'] = krx_stock.pop('itmsNm', None)
                krx_stock['corp_number'] = krx_stock.pop('crno', None)
                krx_stock['corp_name'] = krx_stock.pop('corpNm', None)
                krx_stock['short_isin_code'] = krx_stock.pop('shotnIsin', None)
                krx_stock['face_value'] = krx_stock.pop('stckParPrc', None)
                krx_stock['issue_cnt'] = krx_stock.pop('issuStckCnt', None)
                krx_stock['listing_date'] = krx_stock.pop('lstgDt', None)
                krx_stock['industry'] = None # 산업군(섹터)에 대한 데이터 소스를 찾지 못함

            # Query Execution
            self.insert_items(table='basic_stock_info', columns=['isin_code', 'short_isin_code', 'market_category', 'item_name', 'corp_name', 'corp_number', 'listing_date', 'issue_cnt', 'industry', 'face_value'], data=basic_stock_info)

        except Exception as err_msg:
            print(f"[ERROR] build_basic_stock_info: {err_msg}")

    def build_price_info(self):
        """
        데이터베이스의 price_info 테이블에 KOSPI, KOSDAQ, KONEX에 상장된 전 종목에 대한 주가정보들을 저장한다.
        ※ 본 메서드는 DBA만 수행할 수 있다.
        
        [Parameters]
        -
        
        [Returns]
        -
        """
        
        # DBA Only can run initial building function
        if(self.conn_user != config.ID_DBA):
            print("Only DBA can run the build function")
            return False

        try:
            # Clear Table
            self.delete_item(table='price_info')

            # Listing All Stock
            krx_listed_info = api.get_krx_listed_info(serviceKey=config.API_KEY_OPEN_DATA_PORTAL)

            for kr_stock in krx_listed_info:

                list_ohlcv = api.get_market_ohlcv_by_date(short_isin_code=kr_stock['shotnIsin'])

                for ohlcv in list_ohlcv:
                    ohlcv['isin_code'] = kr_stock['isinCd']
                    ohlcv.pop('short_isin_code')

                self.insert_items(table='price_info', columns=['base_date', 'isin_code', 'market_price', 'close_price', 'high_price', 'low_price', 'fluctuation', 'fluctuation_rate', 'volume'], data=list_ohlcv)
        
        except Exception as err_msg:
            print(f"[ERROR] build_price_info Error: {err_msg}")

    def build_financial_info(self):
        """
        데이터베이스의 financial_info 테이블에 KOSPI, KOSDAQ, KONEX에 상장된 전 종목에 대한 재무정보들을 저장한다.
        ※ 본 메서드는 DBA만 수행할 수 있다.
        
        [Parameters]
        -
        
        [Returns]
        -
        """

        # DBA Only can run initial building function
        if(self.conn_user != config.ID_DBA):
            print("Only DBA can run the build function")
            return False

        try:
            pass # This logic not implemented yet

        except Exception as err_msg:
            print(f"[ERROR] build_financial_info Error: {err_msg}")

    def get_all_data(self, table:str=None):
        """
        테이블의 모든 데이터를 조회한다.

        [Parameters]
        table  (str) : 데이터를 조회할 테이블 이름 (default: None)

        [Returns]
        list : 조회 결과 (list of dict)
        """
        
        try:
            # Query
            return self.find_item(table=table)
        
        except Exception as err_msg:
            print(f"[ERROR] get_all_data Error: {err_msg}")

    def get_isin_code(self, short_isin_code:str):
        """
        ISIN Code에 해당하는 종목의 종가를 조회한다.

        [Parameters]
        isin_code (str) : 국제 증권 식별 번호 (축약형, 6자리)

        [Returns]
        str  : 국제 증권 식별 번호 (12자리)
        """

        try:
            # Query
            result = self.find_item(table='basic_stock_info', columns='isin_code', condition=f"short_isin_code = CAST('{short_isin_code}' AS varchar)")

            return result[0][0]

        except Exception as err_msg:
            print(f"[ERROR] get_isin_code Error: {err_msg}")

    def get_short_isin_code(self, isin_code:str):
        """
        ISIN Code에 해당하는 종목의 종가를 조회한다.

        [Parameters]
        isin_code (str) : 국제 증권 식별 번호 (12자리)

        [Returns]
        str  : 국제 증권 식별 번호 (축약형, 6자리)
        """

        try:
            # Query
            result = self.find_item(table='basic_stock_info', columns='short_isin_code', condition=f"isin_code = CAST('{isin_code}' AS varchar)")

            return result[0][0]

        except Exception as err_msg:
            print(f"[ERROR] get_short_isin_code Error: {err_msg}")

    def get_close_price(self, isin_code:str, start_date:str='20000101', end_date:str=dm.YESTERDAY):
        """
        ISIN Code에 해당하는 종목의 종가를 조회한다.

        [Parameters]
        isin_code  (str) : 국제 증권 식별 번호 (12자리)
        start_date (str) : 조회를 시작할 날짜 (Format: YYYYMMDD) (Default: '20000101')
        end_date   (str) : 조회를 종료할 날짜 (Format: YYYYMMDD) (Default: 전일 (KST 기준))
        
        [Returns]
        list  : 기준일자:종가 Pair들이 저장된 리스트 (list of dict) ex) {'base_date': <기준일자>, 'isin_code':<국제증권식별번호>, 'close_price': <종가>}
        """

        try:
            # Query
            result = self.find_item(table='price_info', columns=['base_date', 'isin_code', 'close_price'], condition=f"isin_code = CAST('{isin_code}' AS varchar) AND CAST('{start_date}' AS date) <= base_date AND base_date <= CAST('{end_date}' AS date)")

            # Parsing
            rows = []
            data = {}
            for row in result:
                raw_string = row[0][1:-1]
                data['base_date'] = raw_string.split(sep=',')[0]
                data['isin_code'] = raw_string.split(sep=',')[1]
                data['close_price'] = int(raw_string.split(sep=',')[2])
                rows.append(data)

            return rows

        except Exception as err_msg:
            print(f"[ERROR] get_close_price Error: {err_msg}")

    def set_news(self, isin_code:str, write_date:str, headline:str, sentiment:float):
        """
        새로운 뉴스 기사를 데이터베이스에 저장한다.
        해당 종목(short_isin_code)에 연관된 뉴스 기사가 50개를 초과할 경우,
        가장 오래된 뉴스 기사를 제거하고 삽입한다.

        [Parameters]
        isin_code  (str)   : 국제 증권 식별 번호 (12자리)
        write_date (str)   : 뉴스 기사 작성 일자 (Format: YYYYMMDD)
        headline   (str)   : 뉴스 헤드라인
        sentiment  (float) : 뉴스 감정도
        
        [Returns]
        int : 해당 뉴스에 부여된 고유번호
        """
        
        try:
            data = {
                'isin_code'  : isin_code,
                'write_date' : write_date,
                'headline'   : headline,
                'sentiment'  : sentiment
            }

            self.insert_item(table='news_info', columns=['isin_code', 'write_date', 'headline', 'sentiment'], data=data)
            return self.find_item(table='news_info', columns='news_id', condition=f"isin_code = CAST('{isin_code}' AS {TYPE_news_info['isin_code']}) AND write_date = CAST('{write_date}' AS {TYPE_news_info['write_date']}) AND headline = CAST('{headline}' AS {TYPE_news_info['headline']})")[0][0]

        except Exception as err_msg:
            print(f"[ERROR] set_news Error: {err_msg}")

    def set_multiple_news(self, news_list:list):
        """
        새로운 다수의 뉴스 기사를 데이터베이스에 저장한다.
        해당 종목(short_isin_code)에 연관된 뉴스 기사가 50개를 초과할 경우,
        가장 오래된 뉴스 기사를 제거하고 삽입한다.

        [Parameters]
        news_list (list) : 저장할 다수의 뉴스들의 정보가 담긴 2차원 리스트 ex) [[<isin_code>, <write_date>, <headline>, <sentiment>], ...]
            isin_code  (str)   : 국제 증권 식별 번호 (12자리)
            write_date (str)   : 뉴스 기사 작성 일자 (Format: YYYYMMDD)
            headline   (str)   : 뉴스 헤드라인
            sentiment  (float) : 뉴스 감정도
        
        [Returns]
        int : 가장 마지막에 저장된 뉴스에 부여된 고유번호
        """
        
        try:

            multiple_news = list()
            last_news = dict()
            for news in news_list:
                data = dict()
                data['isin_code'] = news[0]
                data['write_date'] = news[1]
                data['headline'] = news[2]
                data['sentiment'] = news[3]
                multiple_news.append(data)

                last_news['isin_code'] = news[0]
                last_news['write_date'] = news[1]
                last_news['headline'] = news[2]
                last_news['sentiment'] = news[3]

            self.insert_items(table='news_info', columns=['isin_code', 'write_date', 'headline', 'sentiment'], data=multiple_news)
            return self.find_item(table='news_info', columns='news_id', condition=f"isin_code = CAST('{last_news['isin_code']}' AS {TYPE_news_info['isin_code']}) AND write_date = CAST('{last_news['write_date']}' AS {TYPE_news_info['write_date']}) AND headline = CAST('{last_news['headline']}' AS {TYPE_news_info['headline']})")[0][0]

        except Exception as err_msg:
            print(f"[ERROR] set_multiple_news Error: {err_msg}")

    def set_new_member(self, member_id:str, member_pw:str, member_email:str):
        """
        신규 회원의 정보를 입력받아 데이터베이스에 저장한다.

        [Parameters]
        member_id    (str) : 신규회원 ID
        member_pw    (str) : 신규회원 비밀번호
        member_email (str) : 신규회원 이메일
        
        [Returns]
        True  : 데이터베이스에 중복된 ID가 존재하지 않아 저장에 성공한 경우
        False : 데이터베이스에 중복된 ID가 존재하여, 저장에 실패한 경우
        """

        try:
            # Duplicates Check
            if len(self.find_item(table='member_info', condition=f"member_id = CAST('{member_id}' AS {TYPE_member_info['member_id']})")) > 0: # 해당 아이디가 이미 존재함
                return False
            
            # Parameter Setting
            columns = list(TYPE_member_info.keys())
            data = [member_id, member_pw, member_email]
            signup_data = dict()
            
            for column, value in zip(columns, data):
                signup_data[column] = value

            # Query
            self.insert_item(table='member_info', columns=columns, data=signup_data)

        except Exception as err_msg:
            print(f"[ERROR] set_new_member Error: {err_msg}")
            return False
