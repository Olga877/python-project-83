from psycopg2.extras import RealDictCursor


class UrlRepository:
    def __init__(self, conn):
        self.conn = conn

    def _create(self, url_data):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO urls (name) VALUES (%s) RETURNING id",
                (url_data,)
            )
            url_data['id'] = cur.fetchone()[0]
        self.conn.commit()
        return url_data['id']

    def save(self, url_data):
        if 'id' not in url_data:
            id = self._create(url_data)
            return id

    def find(self, id):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM urls WHERE id = %s", (id,))
            return cur.fetchone()


