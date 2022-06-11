# -----------------------------------------------------------------------------
# Graphic Server Protocol (GSP) — reference implementation
# Copyright 2022 Nicolas P. Rougier - BSD 2 Clauses licence
# -----------------------------------------------------------------------------
import yaml
import base64
import itertools
import numpy as np
from datetime import datetime
from functools import wraps


def command(method=None, record=None, output=None):
    """Function decorator that create a command and optionally record it and/or write it
    to stdout. """

    def wrapper(func):

        @wraps(func)
        def inner(self, *args, **kwargs):
            keys = func.__code__.co_varnames[1:]
            values = args
            
            func(self, *args, **kwargs)

            # Create command
            parameters = {"id": self.id}
            for key, value in zip(keys,values):
                parameters[key] = value
            classname = self.__class__.__name__
            methodname = func.__code__.co_name if method is None else method
            name = "%s/%s" % (classname, methodname) if methodname else classname
            command = Command.write(self, name, parameters)
            if record or Command.record:
                Command.commands.append(command)
            if output or Command.output:
                print(command)
        return inner
    return wrapper

class Object:

    id_counter = itertools.count()
    record = True
    objects = {}

    def __init__(self):
        self.id = 1 + next(Object.id_counter)
        if Object.record:
            Object.objects[self.id] = self

    def __eq__(self, other):
        for key in vars(self).keys():
            if getattr(self, key) != getattr(other, key):
                return False
        return True

class Command:

    record = True
    output = True
    id_counter = itertools.count()
    commands = []

    @classmethod
    def write(cls, self, method, parameters):
        command_id = 1 + next(Command.id_counter)
        timestamp = datetime.timestamp( datetime.now())
        data = [ { "method" : method,
                   "id" : command_id,
                   "timestamp" : timestamp,
                   "parameters" : parameters } ]
        return yaml.dump(data, default_flow_style=None, sort_keys=False)

    @classmethod
    def process(cls, command, globals=None, locals=None):
        data = yaml.safe_load(command)[0]
        try:
            classname, method = data["method"].split("/")
        except ValueError:
            classname, method = data["method"], None
        parameters = data["parameters"]
        
        if method is None:
            object_id = parameters["id"]
            del parameters["id"]
            object = globals[classname](**parameters)
            object.id = object_id
            Object.objects[object_id] = object
        else:
            object_id = parameters["id"]
            del parameters["id"]
            getattr(globals[classname], method)(Object.objects[object_id], **parameters)


def mode(mode="server", reset=True, record=None, output=None):
    "Set protocol in specified mode (server or client)."

    if reset:
        Object.objects = {}
    if mode == "client":
        Command.record = record if record is not None else True
        Command.output = output if output is not None else True
        Object.record = True
    else:
        Command.record = record if record is not None else False
        Command.output = output if output is not None else False
        Object.record = False

def objects():
    return Object.objects

def commands():
    return Command.commands

def process(command, globals=None, locals=None):
    Command.process(command, globals, locals)
