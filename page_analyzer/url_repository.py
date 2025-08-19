from psycopg2.extras import RealDictCursor


class UrlRepository:
    def __init__(self, conn):
        self.conn = conn

    def save(self, url_data):
        with self.conn:
            try:
                with self.conn.cursor() as cur:
                    cur.execute(
                        """
                            INSERT INTO urls (name) VALUES (%s)
                            RETURNING id;""",
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
        with self.conn:
            try:
                with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("SELECT * FROM urls WHERE id=%s;", (id,))
                    return cur.fetchone()
            except Exception:
                return None

    def find_by_name(self, name):
        with self.conn:
            try:
                with self.conn.cursor() as cur:
                    cur.execute("SELECT id FROM urls WHERE name=%s;", (name,))
                    id = cur.fetchone()[0]
                    return id if id else None
            except Exception:
                return None

    def get_checked(self, data, url_info):
        query = """
                    INSERT INTO url_checks 
                    (url_id, status_code, h1, title, description)
                    VALUES (%s, %s, %s, %s, %s) RETURNING id;
                """

        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute(query, (
                    url_info.get('id'),
                    data.get('status'),
                    data.get('h1'),
                    data.get('title'),
                    data.get('description'),
                ))
                self.conn.commit()

    def find_checks(self, id):
        query = "SELECT * FROM url_checks WHERE url_id=%s ORDER BY id DESC;"
        with self.conn:
            try:
                with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, (id,))
                    return cur.fetchall()
            except Exception:
                return None

    def get_content(self):
        query = """
                    SELECT DISTINCT ON (urls.id) 
                        urls.*,
                        COALESCE(url_checks.created_at::TEXT, '') 
                        AS check_date,
                        COALESCE(url_checks.status_code::TEXT, '') 
                        AS status
                    FROM urls
                    LEFT JOIN url_checks ON urls.id = url_checks.url_id
                    ORDER BY urls.id DESC;
                """
        with self.conn:
            try:
                with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query)
                    return cur.fetchall()
            except Exception:
                return None