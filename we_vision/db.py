import mariadb as mdb

# 데이터베이스 연결
class Database:
    def __init__(self, conn_params):
        self.conn_params = conn_params
        self.connect()
        self.reset_tbl_warning()

    # 데이터 베이스 연결
    def connect(self):
        self.db_conn = mdb.connect(**self.conn_params)
        self.cursor = self.db_conn.cursor()
        print("데이터 베이스 연결")

    # 데이터 베이스 연결 끊기
    def disconnect(self):
        self.cursor.close()
        self.db_conn.close()
        print("데이터 베이스 연결 해제")

    # tbl_warning 초기화
    def reset_tbl_warning(self):
        self.cursor.execute("DELETE FROM tbl_warning")

    # tbl_warning 데이터 불러오기
    def get_tbl_warning(self):
        self.cursor.execute("SELECT * FROM tbl_warning")

        # Get results
        result = self.cursor.fetchall()

        return len(result), result

    # tbl_warning에 데이터 삽입
    def put_tbl_warning(self,data):
        insert_query = "INSERT INTO tbl_warning VALUES (?,?,?,?)"
        self.cursor.execute(insert_query, data)

