import os
import psycopg2
import psycopg2.extras

class DatabasePersistence:
    def __init__(self):
        if os.environ.get('FLASK_ENV') == 'production':
            self.connection = psycopg2.connect(os.environ['DATABASE_URL'])
            self._setup_schema()
        else:
            self.connection = psycopg2.connect(dbname="todos")
            self._setup_schema()

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

    def _setup_schema(self):
        with self.connection.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = 'lists';
            """)
            if cur.fetchone()[0] == 0:
                cur.execute("""
                    CREATE TABLE lists (
                        id serial PRIMARY KEY,
                        name text NOT NULL UNIQUE
    );
                """)

            cur.execute("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = 'todos';
            """)
            if cur.fetchone()[0] == 0:
                cur.execute("""
                    CREATE TABLE todos (
                        id serial PRIMARY KEY,
                        name text NOT NULL,
                        completed boolean NOT NULL DEFAULT false,
                        list_id integer NOT NULL REFERENCES lists (id)
                    );
                """)

            self.connection.commit()
