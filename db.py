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
                todos = self._find_todos_for_list(item['id'])
                item.setdefault('todos', todos)
            return lists

    def find_list(self, id):
        with self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM lists WHERE id = %s", (id,))
            list = dict(cur.fetchone())
            todos = self._find_todos_for_list(id)
            list.setdefault('todos', todos)
            return list

    def _find_todos_for_list(self, list_id):
        with self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM todos WHERE list_id = %s", (list_id,))
            return cur.fetchall()