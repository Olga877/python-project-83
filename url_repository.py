from psycopg2.extras import RealDictCursor
import requests


class UrlRepository:
    def __init__(self, conn):
        self.conn = conn

    def save(self, url_data):
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO urls (name) VALUES (%s) RETURNING id;",
                    (url_data,)
                )
                id = cur.fetchone()[0]
            self.conn.commit()
            return id
        except Exception as e:
            self.conn.rollback()
            print(f"Error saving data: {e}")
            return None


    def find(self, id):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM urls WHERE id=%s;", (id,))
            return cur.fetchone()

    def find_by_name(self, name):
        with self.conn.cursor() as cur:
            cur.execute("SELECT id FROM urls WHERE name=%s;", (name,))
            id = cur.fetchone()[0]
            return id if id else None

    def check_url_status(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.status_code
        except requests.exceptions.RequestException as e:
            print(f"Error occurred: {e}")
            return None

    def get_checked(self, id):
        url = self.find(id)['name']
        status = self.check_url_status(url)
        if status:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO url_checks (url_id, status_code) VALUES (%s, %s) RETURNING id;",
                    (id, status)
                )
                check_id = cur.fetchone()[0]
                self.conn.commit()
                return check_id
        else:
            return None

    def find_checks(self, id):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM url_checks WHERE url_id=%s ORDER BY id DESC;", (id,))
            return cur.fetchall()


    def get_content(self):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                            SELECT DISTINCT ON (urls.id) 
                                urls.*,
                                COALESCE(url_checks.created_at::TEXT, '') AS check_date,
                                COALESCE(url_checks.status_code::TEXT, '') AS status
                            FROM urls
                            LEFT JOIN url_checks ON urls.id = url_checks.url_id
                            ORDER BY urls.id DESC;
                        """)
            return cur.fetchall()


    def is_unique(self, url):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM urls WHERE name = %s;",
                (url,)
            )
            name = cur.fetchone()
            if not name:
                return True
            return False




