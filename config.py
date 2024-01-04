import os
import configparser

SETTINGS_FILE = "settings.ini"

DEFAULT_PARAMS = {
    "device": "pc",
    "window": "Rise of Kingdoms",
    "serial": "127.0.0.1:5555",
    "count": "300",
    "dir": os.getcwd(),
    "tag": "KvK-Start",
    "delay": "0.5"
}


def getParameters():
    config = configparser.ConfigParser()
    if len(config.read(SETTINGS_FILE)) == 0:
        # file does not exist
        return DEFAULT_PARAMS
    if "parameters" not in list(config):
        # parameters section not found
        return DEFAULT_PARAMS

    # return the parameters
    readParams = dict(config['parameters'])

    # check if there are any missing parameters
    # fill the missing items from the default
    diff = set(DEFAULT_PARAMS) - set(readParams)
    for k in diff:
        readParams.update({k: DEFAULT_PARAMS[k]})

    return readParams


def setParameters(params):
    config = configparser.ConfigParser()
    config.read(SETTINGS_FILE)
    config['parameters'] = params
    with open(SETTINGS_FILE, 'w') as configfile:  # save
        config.write(configfile)
