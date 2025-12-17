from termcolor import colored
import builtins

original_print = print

def color_of(value):
    if isinstance(value, str):
        return "green"
    elif isinstance(value, int):
        return "yellow"
    elif isinstance(value, float):
        return "cyan"
    elif isinstance(value, bool):
        return "magenta"
    elif value is None:
        return "blue"
    return "white"


def is_simple(value):
    """Return True if value contains NO nested containers."""
    if isinstance(value, (list, tuple, set)):
        return all(not isinstance(v, (list, tuple, set, dict)) for v in value)
    if isinstance(value, dict):
        return all(not isinstance(v, (list, tuple, set, dict)) for v in value.values())
    return True


def format_value(value, indent=0, in_container=False):
    space = " " * indent

    # ===== STRINGS =====
    if isinstance(value, str):
        if in_container:
            return colored(f"'{value}'", color_of(value))
        else:
            return colored(value, "white")

    # ===== NUMBERS / BOOL / NONE =====
    if isinstance(value, (int, float, bool)) or value is None:
        return colored(str(value), color_of(value))

    # ===== LIST / TUPLE / SET =====
    if isinstance(value, (list, tuple, set)):
        opening = "[" if isinstance(value, list) else "(" if isinstance(value, tuple) else "{"
        closing = "]" if isinstance(value, list) else ")" if isinstance(value, tuple) else "}"

        # Single-line if small and simple
        if is_simple(value) and len(str(value)) < 50:
            inside = ", ".join(format_value(v, in_container=True) for v in value)
            return colored(f"{opening}{inside}{closing}", "white")

        # Multi-line
        result = opening + "\n"
        for item in value:
            result += space + "  " + format_value(item, indent + 2, in_container=True) + ",\n"
        result += space + closing
        return colored(result, "white")

    # ===== DICT =====
    if isinstance(value, dict):

        # Single-line if simple & short
        if is_simple(value) and len(str(value)) < 60:
            inside = ", ".join(
                f"{colored(k,'white')}: {format_value(v, in_container=True)}"
                for k, v in value.items()
            )
            return colored("{" + inside + "}", "white")

        # Multi-line pretty print
        result = "{\n"
        for k, v in value.items():
            key = colored(k, "white")
            val = format_value(v, indent + 2, in_container=True)
            result += f"{space}  {key}: {val},\n"
        result += space + "}"
        return colored(result, "white")
    

    if isinstance(value,type):
              
        return colored(value, "magenta")
    if hasattr(value, '__dict__'):
        return colored_print(value.__dict__)

    return colored(str(value), "white")


def colored_print(*args,**kwargs):
    for arg in args:
        original_print(format_value(arg, in_container=False),**kwargs)
    return ''    


def enable():
    """Overwrite built-in print globally."""
    builtins.print = colored_print


if __name__=="__main__":
        d = {
            "name": "Vansh Sharma",
            "age": 20,
            "cgpa": 8.74,
            "is_student": True,
            "skills": [
                "Python",
                "JavaScript",
                "React",
                "Machine Learning",
                ["TensorFlow", "PyTorch"],   # nested list
            ],
            "projects": {
                "music_app": {
                    "using": "React Native",
                    "apis": ["JioSaavn", "YouTube Data API"],
                    "published": False
                },
                "game_dev": {
                    "engine": "Unity",
                    "type": "3D",
                    "levels_completed": 4,
                    "objects": ["car", "trees", "houses"],
                },
                "ml_model": {
                    "dataset": "DailyDialog",
                    "type": "GPT-2 Fine-tuning",
                    "accuracy": 0.89
                }
            },
            "education": {
                "college": "XYZ Engineering College",
                "semester": 2,
                "branch": "CSE (AIML)",
                "subjects": ["Maths", "Chemistry", "DSA", "ML"]
            },
            "favorites": {
                "food": ["pizza", "pasta"],
                "sport": "cricket",
                "color": None,
                "lucky_numbers": [3, 7, 21]
            },
            "random_values": [
                None,
                True,
                999,
                3.14159,
                {"nested_key": "nested_value"},
                {"coords": {"x": 10, "y": 20}}
            ]
            }

        print("Hello", 10, 3.14, True, None, [1,2,3], {"a": 1, "b": [9, 8]})
        print("aloo kha lo")
        print(9)
        print({"a":1, "b":2})

        print([1,2,4])
        print(d)
