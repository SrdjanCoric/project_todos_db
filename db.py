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

    def create_new_list(self, name):
        with self.connection.cursor() as cur:
            cur.execute("INSERT INTO lists (name) VALUES (%s)", (name,))
            self.connection.commit()

    def delete_list(self, id):
        with self.connection.cursor() as cur:
            cur.execute("DELETE FROM todos WHERE list_id = %s", (id,))
            cur.execute("DELETE FROM lists WHERE id = %s", (id,))
            self.connection.commit()

    def update_list_name(self, id, new_name):
        with self.connection.cursor() as cur:
            cur.execute("UPDATE lists SET name = %s WHERE id = %s", (new_name, id,))
            self.connection.commit()

    def create_new_todo(self, list_id, todo_name):
        with self.connection.cursor() as cur:
            cur.execute("INSERT INTO todos (list_id, name) VALUES(%s, %s)", (list_id, todo_name,))
            self.connection.commit()

    def delete_todo_from_list(self, list_id, todo_id):
        with self.connection.cursor() as cur:
            cur.execute("DELETE FROM todos WHERE id = %s AND list_id = %s", (todo_id, list_id,))
            self.connection.commit()

    def update_todo_status(self, list_id, todo_id, new_status):
        with self.connection.cursor() as cur:
            cur.execute("UPDATE todos SET completed = %s WHERE id = %s AND list_id = %s", (new_status, todo_id, list_id,))
            self.connection.commit()

    def mark_all_todos_as_completed(self, list_id):
        with self.connection.cursor() as cur:
            cur.execute("UPDATE todos SET completed = True WHERE list_id = %s ", (list_id,))
            self.connection.commit()

    def _find_todos_for_list(self, id):
        with self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM todos WHERE list_id = %s", (id,))
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
