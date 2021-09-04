"""
A dummy module for testing purpouses
"""
SETTINGS = {
    "Setting1": {
        "Required": True,
        "Value": ["List", "of", "Values"],
        "Description": "This is the description"
    },

    "Setting2": {
        "Required": True,
        "Value": ["List", "of", "Values"],
        "Description": "This is the description for setting2"
    }
}

revision = """
    A good testing module.
"""


def run(*args, **kwargs):
    print("Running")

def set(key, value):
    print("Setting {} = {}".format(key, value))

def params():
    return SETTINGS