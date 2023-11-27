class SessionPersistence:
    def __init__(self, session):
        self.session = session
        if 'lists' not in self.session:
            self.session['lists'] = []

    def find_list(self, id):
        return next((lst for lst in self.session['lists'] if lst['id'] == id), None)

    def all_lists(self):
        return self.session['lists']

    def create_new_list(self, list_name):
        id = self._next_element_id(self.session['lists'])
        self.session['lists'].append({'id': id, 'name': list_name, 'todos': []})
        self.session.modified = True

    def delete_list(self, id):
        self.session['lists'] = [list for list in self.session['lists'] if list['id'] != id]
        self.session.modified = True

    def update_list_name(self, id, new_name):
        list = self.find_list(id)
        if list:
            list['name'] = new_name
            self.session.modified = True

    def create_new_todo(self, list_id, todo_name):
        list = self.find_list(list_id)
        if list is not None:
            id = self._next_element_id(list['todos'])
            list['todos'].append({'id': id, 'name': todo_name, 'completed': False})
            self.session.modified = True

    def delete_todo_from_list(self, list_id, todo_id):
        list = self.find_list(list_id)
        if list is not None:
            list['todos'] = [todo for todo in list['todos'] if todo['id'] != todo_id]
            self.session.modified = True

    def update_todo_status(self, list_id, todo_id, new_status):
        list = self.find_list(list_id)
        if list is not None:
            todo = next((t for t in list['todos'] if t['id'] == todo_id), None)
            if todo:
                todo['completed'] = new_status
                self.session.modified = True

    def mark_all_todos_as_completed(self, list_id):
        list = self.find_list(list_id)
        if list is not None:
            for todo in list['todos']:
                todo['completed'] = True
            self.session.modified = True

    def _next_element_id(self, elements):
        return max([element['id'] for element in elements], default=0) + 1