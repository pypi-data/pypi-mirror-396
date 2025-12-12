import csv
import sqlite3
import os
from dataclasses import dataclass


# 定义返回的数据对象，模仿 uszipcode 的对象风格
@dataclass
class ZipCode:
    zipcode: str
    city: str
    state: str
    state_abbr: str
    county: str
    lat: float
    lng: float

    def to_dict(self):
        return self.__dict__


class SearchEngine:
    def __init__(self, simple_zipcode=True):
        # simple_zipcode 参数只是为了致敬原版库，这里不做复杂处理
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._init_db()

    def _init_db(self):
        """初始化数据库并将CSV加载到内存"""
        # 创建表
        self.cursor.execute("""
                            CREATE TABLE zipcodes
                            (
                                zip        TEXT PRIMARY KEY,
                                city       TEXT,
                                state      TEXT,
                                state_abbr TEXT,
                                county     TEXT,
                                lat        REAL,
                                lng        REAL
                            )
                            """)

        # 获取当前文件所在路径，定位 CSV
        base_path = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(base_path, 'us_zipcodes.csv')

        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Database file not found at {csv_path}")

        # 读取 CSV 并插入数据库
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            to_db = []
            for row in reader:
                to_db.append((
                    row['zip'],
                    row['city'],
                    row['state'],
                    row['state_abbr'],
                    row['county'],
                    float(row['lat']) if row['lat'] else 0.0,
                    float(row['lng']) if row['lng'] else 0.0
                ))

            self.cursor.executemany("""
                                    INSERT
                                    OR IGNORE INTO zipcodes 
                (zip, city, state, state_abbr, county, lat, lng) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
                                    """, to_db)
            self.conn.commit()

            # 创建索引加速查询
            self.cursor.execute("CREATE INDEX idx_city ON zipcodes (city);")
            self.cursor.execute("CREATE INDEX idx_state ON zipcodes (state_abbr);")

    def _row_to_obj(self, row):
        if not row:
            return None
        return ZipCode(
            zipcode=row[0], city=row[1], state=row[2],
            state_abbr=row[3], county=row[4], lat=row[5], lng=row[6]
        )

    def by_zipcode(self, zipcode):
        """按邮编精确查询"""
        self.cursor.execute("SELECT * FROM zipcodes WHERE zip = ?", (str(zipcode),))
        row = self.cursor.fetchone()
        return self._row_to_obj(row)

    def by_city_and_state(self, city=None, state=None):
        """按城市和州查询（支持模糊搜索）"""
        query = "SELECT * FROM zipcodes WHERE 1=1"
        params = []

        if city:
            query += " AND city LIKE ?"
            params.append(f"%{city}%")

        if state:
            query += " AND (state_abbr = ? OR state LIKE ?)"
            params.append(state.upper())
            params.append(f"%{state}%")

        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        return [self._row_to_obj(row) for row in rows]

    def by_prefix(self, prefix):
        """按邮编前缀查询 (如 902)"""
        self.cursor.execute("SELECT * FROM zipcodes WHERE zip LIKE ?", (f"{prefix}%",))
        rows = self.cursor.fetchall()
        return [self._row_to_obj(row) for row in rows]

    def close(self):
        self.conn.close()