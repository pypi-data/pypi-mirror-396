import json

def в_строку(объект):
    return json.dumps(объект, ensure_ascii=False)

def из_строки(строка):
    return json.loads(строка)
