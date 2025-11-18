import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")


def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_user(user_id, user_name=None):
    data = load_data()
    if str(user_id) not in data:
        data[str(user_id)] = {
            "name": user_name or "Unknown",
            "level": 1,
            "xp": 0,
            "resets": 0
        }
        save_data(data)
    return data[str(user_id)]


def update_user(user_id, **kwargs):
    data = load_data()
    user = data.get(str(user_id))
    if not user:
        return None
    for key, value in kwargs.items():
        user[key] = value
    data[str(user_id)] = user
    save_data(data)
    return user


def xp_for_next_level(level):
    return 20 + level * 10
