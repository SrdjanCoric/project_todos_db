from exceptions import ListNotFoundError

def error_for_list_name(name, lists):
    if not 1 <= len(name) <= 100:
        return "The list name must be between 1 and 100 characters"
    elif any(lst['name'] == name for lst in lists):
        return "The list name must be unique."

    return None

def error_for_todo(name):
    if not 1 <= len(name) <= 100:
        return "Todo name must be between 1 and 100 characters"

    return None

def is_list_completed(lst):
    return len(lst['todos']) > 0 and todos_remaining_count(lst) == 0

def list_class(lst):
    if is_list_completed(lst):
        return "complete"
    return ""

def todos_count(lst):
    return len(lst['todos'])

def todos_remaining_count(lst):
    return sum(1 for todo in lst['todos'] if not todo['completed'])

def is_todo_completed(todo):
    return todo['completed']

def sort_items(items, is_completed):
    incomplete_items = [item for item in items if not is_completed(item)]
    complete_items = [item for item in items if is_completed(item)]

    return incomplete_items + complete_items

def load_list(id, lists):
    for lst in lists:
        if lst['id'] == id:
            return lst

    raise ListNotFoundError(f"The specified list with id {id} was not found.")

def find_todo_by_id(todos, id):
    for todo in todos:
        if todo['id'] == id:
            return todo
    return None
    # incomplete_lists = []
    # complete_lists = []

    # for index, lst in enumerate(lists):
    #     if is_list_completed(lst):
    #         complete_lists.append((index, lst))
    #     else:
    #         incomplete_lists.append((index, lst))

    # return incomplete_lists + complete_lists

# def sort_lists(lists):

#     incomplete_lists = [(index, lst) for index, lst in enumerate(lists) if not is_list_completed(lst)]
#     complete_lists = [(index, lst) for index, lst in enumerate(lists) if is_list_completed(lst)]

#     return incomplete_lists + complete_lists

# def sort_todos(todos):
#     incomplete_todos = [(index, todo) for index, todo in enumerate(todos) if not todo['completed']]
#     complete_todos = [(index, todo) for index, todo in enumerate(todos) if todo['completed']]

#     return incomplete_todos + complete_todos

