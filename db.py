import psycopg2
import psycopg2.extras

class DatabasePersistence:
    def __init__(self):
        self.connection = psycopg2.connect(dbname="todos")

    def all_lists(self):
        with self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM lists")
            result = cur.fetchall()
            lists = [dict(result) for result in result]
            for item in lists:
                item.setdefault('todos', [])
            return lists

    def find_list(self, id):
        with self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM lists WHERE id = %s", (id,))
            list = dict(cur.fetchone())
            list.setdefault('todos', [])
            return list
