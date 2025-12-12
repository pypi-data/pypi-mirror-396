"""Yaml backend for tango.databaseds.database.
"""

from __future__ import annotations

import logging
import os
import weakref
import typing

from . import _abstract
from ruamel.yaml import YAML
from collections.abc import MutableSequence, MutableMapping

_logger = logging.getLogger(__name__)


class _YamlNodeList(list):
    def __init__(self, sequence=None, parent=None):
        list.__init__(self)
        if sequence:
            self.extend(sequence)
        self.__parent: weakref.ReferenceType | None
        if parent is not None:
            self.__parent = weakref.ref(parent)
        else:
            self.__parent = None

    def _patch(self, value):
        if isinstance(value, MutableMapping):
            if not isinstance(value, _YamlNode):
                value = _YamlNode(value, parent=self.parent)
        elif isinstance(value, MutableSequence):
            if not isinstance(value, _YamlNodeList):
                value = _YamlNodeList(value, parent=self.parent)
        return value

    def __getitem__(self, key):
        value = list.__getitem__(self, key)
        value2 = self._patch(value)
        if value is not value2:
            self[key] = value2
        return value2

    def __iter__(self):
        for i in range(0, len(self)):
            yield self[i]

    @property
    def parent(self):
        parent = self.__parent
        if parent is None:
            return None
        return parent()


class _YamlNode(_abstract.Node):
    def __init__(self, *args, parent=None, **kwargs):
        self.__dict: dict[str, typing.Any] = {}
        self.__dict.update(*args, **kwargs)
        self.__parent: weakref.ReferenceType | None
        if parent is not None:
            self.__parent = weakref.ref(parent)
        else:
            self.__parent = None

    def _patch(self, value):
        if isinstance(value, MutableMapping):
            if not isinstance(value, _YamlNode):
                value = _YamlNode(value, parent=self)
        elif isinstance(value, MutableSequence):
            if not isinstance(value, _YamlNodeList):
                value = _YamlNodeList(value, parent=self)
        return value

    def __getitem__(self, key):
        value = self.__dict.__getitem__(key)
        value2 = self._patch(value)
        if value is not value2:
            self.__dict[key] = value2
        return value2

    def __setitem__(self, key, value):
        self.__dict.__setitem__(key, value)

    def __delitem__(self, key):
        self.__dict.__delitem__(key)

    def __contains__(self, key):
        return self.__dict.__contains__(key)

    def pop(self, key, *args, **kwargs):
        value = self.__dict.pop(key, *args, **kwargs)
        value2 = self._patch(value)
        return value2

    def get(self, key, default=None):
        value = self.__dict.get(key, default)
        value2 = self._patch(value)
        if value is not value2:
            self.__dict[key] = value2
        elif key not in self.__dict:
            self.__dict[key] = value2
        return value2

    def setdefault(self, key, *args, **kwargs):
        return self.__dict.setdefault(key, *args, **kwargs)

    def update(self, arg={}, **kwargs):
        self.__dict.update(arg)
        if kwargs:
            self.__dict.update(kwargs)

    def __iter__(self):
        for i in self.__dict:
            yield i

    def __len__(self):
        return len(self.__dict)

    @property
    def parent(self):
        parent = self.__parent
        if parent is None:
            return None
        return parent()

    def __hash__(self):
        return id(self).__hash__()

    def set(self, values: dict[str, typing.Any]):
        self.update(values)

    def get_all(self):
        return dict(self.__dict)

    def save(self):
        pass


class FiltrableDict(dict):
    def keys(self, filter_key=None):
        if filter is None:
            return super(FiltrableDict, self).keys()
        ks = super(FiltrableDict, self).keys()
        return _abstract.list_filter(filter_key, ks)


class YamlDataSource(_abstract.DataSource):
    def __init__(self, personal_name):
        options = self.get_options()
        if len(options.db_access) < 2:
            raise RuntimeError(
                "Path is not specified in the connector param (yaml:path)"
            )
        yaml_root = options.db_access[1]
        if not os.path.exists(yaml_root):
            raise RuntimeError(f"Path '{yaml_root}' do not exists")
        if not os.path.isdir(yaml_root):
            raise RuntimeError(f"Path '{yaml_root}' is not a directory")
        self._yaml_root = yaml_root
        _abstract.DataSource.__init__(self, personal_name)

    def _init_db(self):
        nodes: list[_YamlNode | _YamlNodeList] = []
        for meta in self._iter_data_source():
            if isinstance(meta, MutableSequence):
                nl = _YamlNodeList(meta)
                nodes.append(nl)
            else:
                n = _YamlNode(meta)
                nodes.append(n)
        self._nodes = nodes
        self._devices_info = FiltrableDict()
        self._class_attribute = {}
        self._property_attr_device = {}
        self._aliases = {}

    def _get_root_node(self):
        return self._nodes

    def create_empty(self, parent=None, path=None):
        return _YamlNode(parent=parent)

    def create_device(self, device_info, parent=None):
        return _YamlNode(device_info, parent=parent)

    def _iter_data_source(self):
        parser = YAML(pure=True)
        for root, _dirs, files in os.walk(self._yaml_root, followlinks=True):
            if "__init__.yml" in files:
                files.remove("__init__.yml")
                files.insert(0, "__init__.yml")
            for file in files:
                filename, file_extension = os.path.splitext(file)
                if not (file_extension in [".yml", ".yaml"]):
                    continue
                path = os.path.join(root, file)
                _logger.debug("Read Yaml filename %s", path)
                with open(path, "rt", encoding="utf-8") as f:
                    meta = parser.load(f)
                    yield meta

    def get_node(self, refname):
        node = self.tango_name_2_node[refname]
        if not isinstance(node, _YamlNode):
            node = _YamlNode(node)
            self.tango_name_2_node[refname] = node
        return node

    def create_class_filename(self, class_name):
        _logger.warning("create_class_filename '%s' is not persistant", class_name)
        node = _YamlNode()
        return node

    def create_server_filename(self, server_name):
        _logger.warning("create_server_filename '%s' is not persistant", server_name)
        node = _YamlNode()
        return node

    def get_attr_alias_mapping(self):
        return self._aliases

    def get_class_attribute_list(self, class_name, wildcard):
        return []

    def get_class_attribute(self, klass_name, attr_name):
        key_name = "%s.%s" % (klass_name, attr_name)
        attrs = self._class_attribute.get(key_name, None)
        if attrs is None:
            attrs = _YamlNode()
            self._class_attribute[key_name] = attrs
        return attrs

    def get_property_attr_device(self, dev_name):
        key_name = dev_name.lower().replace("/", ".")
        attrs = self._property_attr_device.get(key_name, None)
        if attrs is None:
            attrs = {}
            self._property_attr_device[key_name] = attrs
        if not isinstance(attrs, _YamlNode):
            attrs = _YamlNode(attrs)
        return attrs

    def get_devices_info(self):
        return self._devices_info

    def get_exported_device_info(self, dev_name):
        info = self._devices_info.get(dev_name)
        if info is None:
            info = _YamlNode()
            self._devices_info[dev_name] = info
        return info

    def get_exported_devices_keys(self, key_filter):
        return self._devices_info.keys(key_filter)

    def __str__(self):
        result = []
        for i in self._get_root_node():
            result.append(str(i))
        return "; ".join(result)


class yaml(_abstract.dbapi):

    DB_API_NAME = "yaml"

    def _create_data_source(self, personal_name):
        return YamlDataSource(personal_name=personal_name)


def get_db(personal_name="", **keys):
    return yaml(personal_name=personal_name)


def get_wildcard_replacement():
    return False
