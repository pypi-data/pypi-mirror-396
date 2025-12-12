# !/usr/bin/python
# -*- coding: utf-8 -*-
import inspect
import json
import datetime
import traceback
from abc import ABC, abstractmethod
import hashlib

class BaseModel(ABC):

    def _get_not_null_fields(self):
        doc = str(self.__doc__)
        if doc == '': return
        doc_lines = doc.splitlines()
        for line in doc_lines:
            if '@NotNull=' in line:
                aux = line[13:]
                return aux.split(',')
        return []
    
    def _get_max_size_fields(self):
        doc = str(self.__doc__)
        if doc == '': return
        doc_lines = doc.splitlines()
        for line in doc_lines:
            if '@Max=' in line:
                aux = line[9:]
                return aux.split(',')
        return []
    
    def _get_timestamp_fields(self):
        doc = str(self.__doc__)
        if doc == '': return
        doc_lines = doc.splitlines()
        for line in doc_lines:
            if '@Timestamp=' in line:
                aux = line[15:]
                return aux.split(',')
        return []
   
    def show_attributes(self):
        field_list = self._get_not_null_fields()
        for field in field_list:
            print("Not NULL: %s " % field)
        field_list = self._get_max_size_fields()
        for field in field_list:
            print("Max Size: %s " % field)
        for i in inspect.getmembers(self):
            if not i[0].startswith('_') and not inspect.ismethod(i[1]):
                print(i)
        
    def _get_field_value(self, name):
        for i in inspect.getmembers(self):
            # Ignores anything starting with underscore 
            # (that is, private and protected attributes)
            if not i[0].startswith('_'):
                # Ignores methods
                if not inspect.ismethod(i[1]):
                    if (i[0] == name):
                        return i[1]
        return None
   
    def validate(self):
        msg = ""
        field_list = self._get_not_null_fields()
        for field in field_list:
            if self._get_field_value(field) == None:
                msg = msg + "Campo %s não pode ser vazio \n" % field
        
        field_list = self._get_max_size_fields()
        for field in field_list:
            field_att = field.split(":")
            field_value = self._get_field_value(field_att[0])
            if field_value != None and len(str(field_value)) > int(field_att[1]):
                msg += "Campo %s não pode ser maior do que %s \n" % (field_att[0], field_att[1])
        if len(msg) > 0:
            raise Exception(msg)
    
    @abstractmethod
    def serialize(self):
        pass

    def set_field_value(self, content):
        timestamp_fields = self._get_timestamp_fields()
        for i in inspect.getmembers(self):
            # Ignores anything starting with underscore 
            # (that is, private and protected attributes)
            if not i[0].startswith('_'):
                # Ignores methods
                if not inspect.ismethod(i[1]):
                    field_name = i[0]
                    if (field_name in content):
                        if (field_name in timestamp_fields and not isinstance(content[field_name], (datetime.date, datetime.datetime))):
                            unix_timestamp = content[field_name]
                            if unix_timestamp != None: 
                                if len(str(unix_timestamp)) > 10:
                                    unix_timestamp = int(unix_timestamp)/1000
                                setattr(self, field_name, datetime.datetime.utcfromtimestamp(unix_timestamp))
                            else:
                                setattr(self, field_name, None)
                        else:    
                            setattr(self, field_name, content[field_name])
    
    def load_json(self, content):
        self.set_field_value(content)

    def toJSON(self):
        try:
            return json.dumps(
                self,
                cls=CustomJSONEncoder)
        except Exception as e:
                print("Erro ao converter a model %s para JSON: %s" % (type(self).__name__, str(e)))
                traceback.print_exc()

    def get_hash(self):
        # Concatenate string representations of attributes
        attributes_string = ''.join(f"{attr}={getattr(self, attr)}" for attr in vars(self))

        # Generate hash using sha256 algorithm
        hash_object = hashlib.sha256(attributes_string.encode())
        return hash_object.hexdigest()

from json import JSONEncoder

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if issubclass(type(obj), BaseModel):
            return obj.__dict__
        elif isinstance(obj, (datetime.date, datetime.datetime, datetime)):
            return int(obj.timestamp() * 1000)
        return JSONEncoder.default(self, obj)