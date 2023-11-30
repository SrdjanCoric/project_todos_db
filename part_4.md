```py
def all_lists(self):
    with self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        # Query to fetch lists and their associated todos in one go
        cur.execute("""
            SELECT lists.*, todos.id as todo_id, todos.name as todo_name, todos.completed as todo_completed
            FROM lists
            LEFT JOIN todos ON lists.id = todos.list_id
        """)
        result = cur.fetchall()

        lists = {}
        for row in result:
            list_id = row['id']
            if list_id not in lists:
                lists[list_id] = {'id': list_id, 'name': row['name'], 'todos': []}
            if row['todo_id'] is not None:
                lists[list_id]['todos'].append({'id': row['todo_id'], 'name': row['todo_name'], 'completed': row['todo_completed']})

        return list(lists.values())

def find_list(self, id):
    with self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("""
            SELECT lists.*, todos.id as todo_id, todos.name as todo_name, todos.completed as todo_completed
            FROM lists
            LEFT JOIN todos ON lists.id = todos.list_id
            WHERE lists.id = %s
        """, (id,))
        result = cur.fetchall()

        list_dict = None
        for row in result:
            if list_dict is None:
                list_dict = {'id': row['id'], 'name': row['name'], 'todos': []}
            if row['todo_id'] is not None:
                list_dict['todos'].append({'id': row['todo_id'], 'name': row['todo_name'], 'completed': row['todo_completed']})

        return list_dict

```