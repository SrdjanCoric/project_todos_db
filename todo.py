from flask import (
    Flask, session, render_template,
    url_for, redirect, request, flash, jsonify
)

import secrets

from utils import (
    error_for_list_name, error_for_todo, list_class, is_list_completed,
    todos_remaining_count, todos_count, sort_items, is_todo_completed,
    load_list, find_todo_by_id
)

from uuid import uuid4, UUID

from exceptions import ListNotFoundError

app = Flask(__name__)

app.secret_key = secrets.token_hex(32)

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


@app.context_processor
def list_utilities_processor():
    return dict(is_list_completed=is_list_completed,
                list_class=list_class, todos_count=todos_count,
                todos_remaining_count=todos_remaining_count,
                sort_items=sort_items, is_todo_completed=is_todo_completed
            )

@app.errorhandler(ListNotFoundError)
def handle_list_not_found_error(error):
    flash(error.message, "error")
    return redirect(url_for('show_lists'))

@app.before_request
def before_request():
    if 'lists' not in session:
        session['lists'] = []


@app.route("/")
def index():
    return redirect(url_for('show_lists'))

@app.route("/lists", methods=["GET"])
def show_lists():
    lists = session['lists']
    return render_template('lists.html', lists=lists)

@app.route("/lists", methods=["POST"])
def create_list():
    name = request.form["list_name"].strip()
    error = error_for_list_name(name, session['lists'])
    if error:
        flash(error, "error")
        return render_template('new_list.html')
    list_id = str(uuid4())
    session['lists'].append({'id': list_id, 'name': name, 'todos': []})
    flash("The list has been created.", "success")
    session.modified = True
    return redirect(url_for('show_lists'))

@app.route("/lists/new")
def add_list():
    return render_template('new_list.html')

@app.route("/lists/<id>", methods=["GET"])
def show_list(id):
    lst = load_list(id, session['lists'])
    return render_template('list.html', list=lst, list_id=id)

@app.route("/lists/<id>", methods=["POST"])
def update_list(id):
    name = request.form["list_name"].strip()
    list = load_list(id, session['lists'])
    error = error_for_list_name(name, session['lists'])
    if error:
        flash(error, "error")
        return render_template('edit_list.html', list=list)
    list['name'] = name
    flash("The list has been updated.", "success")
    session.modified = True
    return redirect(url_for('show_lists'))

@app.route("/lists/<id>/edit")
def edit_list(id):
    list = load_list(id, session['lists'])
    return render_template('edit_list.html', list=list)

@app.route("/lists/<id>/delete", methods=["POST"])
def delete_list(id):
    lists = session['lists']
    for idx in range(len(lists)):
        if lists[idx]['id'] == id:
            del lists[idx]
            break
    flash("The list has been deleted.", "success")
    session.modified = True
    return redirect(url_for('show_lists'))

@app.route("/lists/<list_id>/todos", methods=["POST"])
def create_todo(list_id):
    todo_name = request.form["todo"].strip()
    list = load_list(list_id, session['lists'])

    error = error_for_todo(todo_name)
    if error:
        flash(error, "error")
        return render_template('list.html', list=list, list_id=list_id)
    todo_id = str(uuid4())
    list['todos'].append({'id': todo_id, 'name': todo_name, 'completed': False})
    flash("The todo was added.", "success")
    session.modified = True
    return redirect(url_for('show_list', id=list_id))

@app.route("/lists/<list_id>/todos/<id>/delete", methods=["POST"])
def delete_todo(list_id, id):
    lst = load_list(list_id, session['lists'])
    for idx, todo in enumerate(lst['todos']):
        if todo['id'] == id:
            del lst['todos'][idx]
            break
    session.modified = True
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(success=True)
    else:
        flash("The todo has been deleted.", "success")
        return redirect(url_for('show_list', id=list_id))

@app.route("/lists/<list_id>/todos/<id>", methods=["POST"])
def update_todo_status(list_id, id):
    list = load_list(list_id, session['lists'])
    is_completed = request.form['completed'] == 'True'

    todo = find_todo_by_id(list['todos'], id)
    todo['completed'] = is_completed

    flash("The todo has been updated.", "success")
    session.modified = True
    return redirect(url_for('show_list', id=list_id))

@app.route("/lists/<id>/complete_all", methods=["POST"])
def mark_all_todos_completed(id):
    list = load_list(id, session['lists'])
    for todo in list['todos']:
        todo['completed'] = True

    flash("All todos have been updated.", "success")
    session.modified = True
    return redirect(url_for('show_list', id=id))

if __name__ == "__main__":
    app.run(debug=True, port=5003)
