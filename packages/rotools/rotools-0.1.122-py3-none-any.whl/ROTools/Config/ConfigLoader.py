import os
from pathlib import Path

import yaml

from ROTools.Config.Config import Config
from ROTools.Helpers.DictObj import DictObj


def load_config(config_file):
    import yaml
    return Config(DictObj(yaml.safe_load(open(config_file))))

def load_config_directory(directory, config_file):
    import yaml
    files = os.listdir(directory)
    files = [a for a in files if not a.startswith("_")]
    files = [file for file in files if os.path.isfile(os.path.join(directory, file))]
    files = [os.path.join(directory, a) for a in files if a.endswith(('.yaml', '.yml'))]

    main_file_name = os.path.join(directory, config_file)
    if main_file_name not in files:
        raise Exception("Config file not found!")

    files = [a for a in files if a != main_file_name]

    config = Config(DictObj(yaml.safe_load(open(main_file_name))))

    for file in files:
        sub_config = DictObj(yaml.safe_load(open(file)))
        for key, value in sub_config.items():
            config.set(key, value)

    return config

def process_services(config):
    from pathlib import Path
    from ROTools.Helpers.DictObj import DictObj
    import yaml

    if not config.has("services.config_files"):
        return

    files = [Path(a) for a in config.get("services.config_files", [])]
    files = [a for a in files if a.exists()]
    if len(files) == 0:
        raise Exception("No services config files found!")

    config.services.rem("config_files")

    services = DictObj(yaml.safe_load(open(files[0])))

    for key, value in [(a, b) for a, b in services.items() if b.has("ref_name")]:
        service_config = services.get(value.ref_name, throw=True)

        value.rem("ref_name", throw=False)

        for key2, value2 in service_config.items():
            value.set(key2, value2)


    for key, value in config.services.items():
        ref_name = value if isinstance(value, str) else value.get("ref_name", throw=True)
        service_config = services.get(ref_name, throw=True)
        if isinstance(value, DictObj):
            value.rem("ref_name")

        if isinstance(value, str):
            value = DictObj()
            config.services.set(key, value)

        for key2, value2 in service_config.items():
            value.set(key2, value2)

