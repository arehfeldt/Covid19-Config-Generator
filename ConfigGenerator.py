import requests
import os
import json

base = "https://ephtracking.cdc.gov/apigateway/api/v1/"
content_url = "contentareas/json"
indicator_url = "indicators/"
measure_url = "measures/"
config = []
cache = {}
terminal_padding = 25
defaults = {
    "bar": True,
    "heatMap": True,
    "measureType": "count",
    "normalFactor": 1,
    "group": "No Group",
    "multiplier": 1
}
modifiable = [k for k in defaults.keys()] + ['name', 'stateFromCounty']


def pad_terminal():
    for line in range(terminal_padding):
        print()


def continue_message(message=""):
    input(message + "\n(Enter to continue)")


def yes_or_no(message):
    return input(message + " ('y' or anything else): ") == 'y'


def set_value(k, default_value, measure_name=None, type="string"):
    while True:
        pad_terminal()
        print(f"{k}: {default_value}")
        if yes_or_no(f"Would you like to change the default value of '{k}'" +
                     (f" for '{measure_name}'\n" if measure_name is not None else "\n")):
            if type == 'int':
                default_value = set_int(k, measure_name)
            elif type == 'bool':
                default_value = set_bool(k, measure_name)
            else:
                default_value = set_string(k, measure_name)
        else:
            break
    return default_value


def set_string(k, measure_name=None):
    while True:
        default_value = input(f"Give new value for '{k}': ")
        if len(default_value) > 0: break
        print("New value must not be an empty string!")
    return default_value


def set_int(k, default_value, measure_name=None):
    while True:
        default_value = input(f"Give new value for '{k}' (must be an integer): ").title()
        if default_value.isdigit(): break
        print("New value must be an integer")
    return int(default_value)


def set_bool(k, default_value, measure_name=None):
    while True:
        default_value = input(f"Give new value for '{k}' (t/f): ").title()
        true_list = ['t', 'T', 'true', 'True']
        false_list = ['f', 'F', 'false', 'False']
        if default_value in false_list: return False
        if default_value in true_list: return True
        print("New value must be one of the following")
        print(true_list + false_list)
    return default_value


def get_new_info(url, save_to_cache=True):
    if url in cache: return cache[url]
    data = json.loads(requests.get(url).text)
    if save_to_cache:
        cache.setdefault(url, data)
    return data


def get_content_area():
    pad_terminal()
    print("\nContent Areas:")
    return select_by_id(get_new_info(base + content_url))


def get_indicator(content_area):
    pad_terminal()
    print("\nIndicators:")
    return select_by_id(get_new_info(base + indicator_url + content_area))


def get_measure(indicator):
    pad_terminal()
    print("\nMeasures:")
    return select_by_id(get_new_info(base + measure_url + indicator))


def sort_by_name(ls):
    return sorted(ls, key=lambda x: (x['name']))


def print_list(ls):
    pad_terminal()
    sorted_l = sort_by_name(ls)
    ids = [x['id'] for x in sorted_l]
    names = [x['name'] for x in sorted_l]
    for i in range(len(names)):
        print(f"{ids[i]}\t{names[i]}")


def select_by_id(ls):
    ls = [x for x in ls if x['id'] not in [y['id'] for y in config]]
    ids = [x['id'] for x in ls]
    print_list(ls)
    while True:
        choice = input("Submit id you want to select or 'x' to go back: ")
        if choice in ids: return next((x for x in ls if x['id'] == choice))
        if choice == 'x': break
        print("Not a valid id")
    return None


def state_or_county(measure_id):
    state = 1 in [x['id'] for x in get_new_info(base + f"stratificationlevel/{measure_id}/1/0", save_to_cache=False)]
    county = 2 in [x['id'] for x in get_new_info(base + f"stratificationlevel/{measure_id}/2/0", save_to_cache=False)]
    return state, county


def is_daily(measure_id, strat_by_state):
    data = get_new_info(base + f"temporal/{measure_id}/{1 if strat_by_state else 2}/ALL/ALL", save_to_cache=False)[0]
    return data['childTemporalType'] == "Day"


# test if measure can be stratified by state or county
def measure_valid(measure_id):
    state, county = state_or_county(measure_id)
    if state or county:
        return True
    continue_message("Measure cannot be stratified by state or county!\nYou must select another")
    return False


def get_new_measure():
    while True:  # select content area
        content = get_content_area()
        if content is None: break
        while True:  # select indicator area
            indicator = get_indicator(content['id'])
            if indicator is None: break
            while True:  # select measure area
                measure = get_measure(indicator['id'])
                if measure is None: break
                # check measure is correct and valid
                pad_terminal()
                print(
                    f"\nYou selected:\n{content['id']}: {content['name']}\n"
                    f"\t{indicator['id']}: {indicator['name']}\n"
                    f"\t\t{measure['id']}: {measure['name']}"
                )
                if yes_or_no("\nIs this correct"):
                    if measure_valid(measure['id']): return measure
    return None


def init_measure(measure):
    state, county = state_or_county(measure['id'])
    isDaily = is_daily(measure['id'], state)
    modified_measure = {
        "id": measure['id'],
        "name": set_value("name", measure['name'].title()),
        "state": state,
        "county": county,
        "daily": isDaily,
        "stateFromCounty": False if state or (not county) else set_value("stateFromCounty", ((not state) and county),
                                                                         measure_name=measure['name'], type='bool'),
        "bar": set_value("bar", defaults["bar"], measure_name=measure['name'], type='bool'),
        "line": set_value("line", isDaily, measure['name'], type='bool'),
        "heatMap": set_value("heat map", defaults["heatMap"], measure_name=measure['name'], type='bool'),
        "measureType": set_value("measure summation type", defaults["measureType"], measure_name=measure['name']),
        "normalFactor": set_value("normalization factor", defaults["normalFactor"], measure_name=measure['name'],
                                  type='int'),
        "group": set_value("group", defaults["group"], measure_name=measure['name']),
        "multiplier": 1 if set_value("positive correlation", True, measure_name=measure['name'], type='bool') else -1,
    }
    return modified_measure


def add_new_measures():
    while True:
        measure = get_new_measure()
        if measure is not None:
            pad_terminal()
            measure = init_measure(measure)
            k = 'name'
            config.append(measure)
            continue_message(f"successfully appended '{measure[k]}' to config.")
        else:
            print("No measure selected.")
        if not yes_or_no("\nAdd another measure?"): break


def modify_current_measures():
    continue_message("modify_current_measures is not yet implemented.")
    return None


def publish_config():
    global config
    config = sort_by_name(config)
    output_file = input(
        "Enter name of config file you wish to publish to\n(This will overwrite any existing file be careful!): ")
    with open(output_file, 'w+') as w:
        w.write(json.dumps({"config": config}))
    continue_message(f"Published config to {output_file}")
    return None


def read_config(in_file):
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    try:
        with open(os.path.join(__location__, in_file), 'r') as f:
            new_config = json.load(f)
        return new_config['config']
    except:
        continue_message(f"Unable to read {in_file}, make sure you spelled it correctly or have the correct directory")
        return None


def append_config():
    if not yes_or_no("Are you sure you want to append a new config to the current config?"):
        continue_message("Aborted Append")
        return
    in_file = input("Enter directory/name of config you wish to append: ")
    new_config = read_config(in_file)
    if new_config is None: return
    global config
    for x in new_config:
        config.append(x)
    continue_message(f"Successfully appended {in_file} to working config.")


def load_config():
    pad_terminal()
    if not yes_or_no("Are you sure you want to overwrite your current config"):
        continue_message("Aborted Load")
        return
    in_file = input("Enter directory/name of config you wish to load: ")
    new_config = read_config(in_file)
    if new_config is None: return
    global config
    config = new_config
    continue_message(f"Successfully loaded {in_file} as working config. Original config was deleted.")


def print_entry(entry):
    max_key_length = max([len(k) for k in entry.keys()])
    print(f"\n{entry['name']}")
    for k in entry.keys():
        if k != 'name': print(f"\t{k:{max_key_length}}\t{entry[k]}")


def print_config():
    global config
    config = sort_by_name(config)
    pad_terminal()
    print("Current Config:")
    for entry in config:
        print_entry(entry)


def view_config():
    print_config()
    continue_message()


def clear_config():
    pad_terminal()
    if not yes_or_no("Are you sure you want to clear your current working config"):
        pad_terminal()
        continue_message("Aborted Clear")
        return
    global config
    config = []


def finish():
    print_config()
    if yes_or_no("Would you like to publish this config before exiting?"): publish_config()
    exit(0)


options = {
    view_config: "Print current working config to the terminal.",
    add_new_measures: "Add new measures from NEPHTN API to config.",
    modify_current_measures: "Modify measures of current working config",
    load_config: "Load a config from disk and overwrite current config.",
    append_config: "Load config from disk and append to current config.",
    clear_config: "Clear current working config",
    publish_config: "Write current working config to a file"
}

descriptions = {
    'x': "Exit and optionally publish current working config to a file"
}

choices = {
    'x': finish
}

for i, k in enumerate(options.keys()):
    descriptions.setdefault(str(i + 1), options[k])
    choices.setdefault(str(i + 1), k)

descriptions = sorted(descriptions.items())

while True:
    pad_terminal()
    for entry in descriptions:
        print(f"{entry[0]}: {entry[1]}")
    function = choices.get(input("Submit your choice: "))
    if function is None:
        pad_terminal()
        continue_message("Not a valid choice, please try again.")
    else:
        function()
