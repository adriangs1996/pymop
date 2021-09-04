"""A dummy module for testing purpouses"""


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

revision = "Normal"


def run(*args, **kwargs):
    print("Hacking something")

def set(key, value):
    print("Setting {} = {}".format(key, value))

def params():
    return SETTINGS