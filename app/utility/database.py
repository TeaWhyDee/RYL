from app.db.database import Base


def check_model_difference(instance: Base, json_data):
    check_passed = False

    for key in json_data:
        if key == "note":
            continue
        if getattr(instance, key) != json_data[key]:
            check_passed = True
            break

    return check_passed
