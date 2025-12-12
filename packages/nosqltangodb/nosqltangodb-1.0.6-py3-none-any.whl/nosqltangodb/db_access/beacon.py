"""Beacon backend for tango.databaseds.database.

It has been moved at different places during the time.

See:

- https://github.com/tango-controls/pytango/blob/a8f6a3bfbf547f5b1bb22772280f0eb6e655486f/tango/databaseds/db_access/beacon.py
- https://gitlab.esrf.fr/bliss/bliss/-/commit/c17bcc328d337de856449e3826023dc9f7dac858
"""

import logging
from . import _abstract
from bliss.config import static, settings

_logger = logging.getLogger(__name__)


def _bytes2str_iter(it):
    for k in it:
        yield k.decode()


class _BeaconDataSource(_abstract.DataSource):

    def _init_db(self):
        self._config = static.Config("", 3.0)

    def _get_root_node(self):
        tango = self._config.root["tango"]
        return tango

    def create_empty(self, parent=None, path=None):
        if parent is None:
            parent = self._get_root_node()
        return static.ConfigNode(parent=parent, path=path)

    def create_server_filename(self, server_name):
        filename = f"tango/{server_name.replace('/','_')}.yml"
        server_node = static.ConfigNode(self._config.root, filename=filename)
        return server_node

    def create_class_filename(self, class_name):
        filename = f"tango/{class_name.replace('/','_')}.yml"
        class_node = static.ConfigNode(self._config.root, filename=filename)
        return class_node

    def get_node(self, refname):
        return self._config.get_config(refname)

    def get_attr_alias_mapping(self):
        return settings.HashObjSetting("tango.attr.alias")

    def create_device(self, device_info, parent=None):
        return device_info

    def get_class_attribute_list(self, class_name, wildcard):
        redis = settings.get_redis_proxy()
        attributes = list(
            _bytes2str_iter(
                redis.scan_iter(match="tango.class.attribute.%s" % class_name)
            )
        )
        return _abstract.list_filter(wildcard, attributes)

    def get_class_attribute(self, klass_name, attr_name):
        _logger.debug(
            "get_class_attribute(klass_name=%s,attr_name=%s)", klass_name, attr_name
        )
        key_name = "tango.class.attribute.%s.%s" % (klass_name, attr_name)
        return settings.HashObjSetting(key_name)

    def get_property_attr_device(self, dev_name):
        key_name = "tango.%s" % dev_name.lower().replace("/", ".")
        return settings.HashObjSetting(key_name)

    def get_exported_device_info(self, dev_name):
        key_name = "tango.info.%s" % dev_name
        return settings.HashSetting(key_name)

    def get_exported_devices_keys(self, key_filter):
        cache = settings.get_redis_proxy()
        exported_devices = cache.keys(f"tango.info.{key_filter}")
        return [x.replace("tango.info.", "") for x in _bytes2str_iter(exported_devices)]


class beacon(_abstract.dbapi):

    DB_API_NAME = "beacon"

    def _create_data_source(self, personal_name):
        return _BeaconDataSource(personal_name=personal_name)


def get_db(personal_name="", **keys):
    return beacon(personal_name=personal_name)


def get_wildcard_replacement():
    return False
