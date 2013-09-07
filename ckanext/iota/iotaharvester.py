# -*- coding: utf-8 -*-
import urllib2
import hashlib
import json
import logging
import os.path

import ckan.model
import ckan.lib.base
import ckan.logic
import ckanext.harvest.model
import ckanext.harvest.harvesters

log = logging.getLogger(__name__)
HarvestObject = ckanext.harvest.model.HarvestObject
HarvesterBase = ckanext.harvest.harvesters.HarvesterBase


class IotaHarvester(HarvesterBase):
    '''
    A Harvester for Iota instances
    '''

    # Default to API_VERSION 1 so we can choose groups based on their name,
    # and not their ID
    DEFAULT_API_VERSION = 1

    def info(self):
        return {
            'name': 'iota',
            'title': 'Iota',
            'description': 'Harvests Iota instances'
        }

    def validate_config(self, config_str):
        if not config_str: return

        config = json.loads(config_str)
        api_version = config.get('api_version', self.DEFAULT_API_VERSION)
        groups = config.get('groups', [])

        self._validate_config_options(config)
        self._validate_api_version(api_version)
        self._validate_groups(groups, api_version)

        return config

    def _validate_api_version(self, api_version):
        try:
            int(api_version)
        except ValueError:
            raise ValueError('api_version must be an integer')

    def _validate_groups(self, groups, api_version):
        if not isinstance(groups, list):
            raise ValueError('group must by a list')

        context = {
            'model': ckan.model,
            'user': ckan.lib.base.c.user
        }
        group_key = 'name' if int(api_version) == 1 else 'id'
        group_show = ckan.logic.get_action('group_show')
        for group_value in groups:
            try:
                group_dict = { 'id': group_value }
                group_show(context, group_dict)
            except ckan.logic.NotFound as e:
                msg = 'Group with {key} "{value}" not found. Maybe the \
                api_version (currently {api_version}) is wrong?'
                raise ckan.logic.NotFound(msg.format(key=group_key,
                    value=group_value, api_version=api_version))

    def _validate_config_options(self, config):
        VALID_OPTIONS = ['api_version', 'groups']
        config_options = config.keys()

        invalid_options = list(set(config_options) - set(VALID_OPTIONS))
        if invalid_options:
            msg = 'Invalid options: {options}. The valid options are: \
                {valid_options}'
            raise ValueError(msg.format(options=invalid_options,
                valid_options=VALID_OPTIONS))

    def gather_stage(self, harvest_job):
        log.debug('In IotaHarvester gather_stage (%s)' % harvest_job.source.url)

        package_url = harvest_job.source.url
        objects = []
        related_packages = self._get_related_packages(package_url)
        packages_urls = [package_url] + related_packages
        for package_url in packages_urls:
            base_url = package_url.rstrip('/')
            guid = base_url
            obj = HarvestObject(guid = guid, job = harvest_job)
            obj.save()
            objects.append(obj)

        object_ids = [obj.id for obj in objects]
        log.debug('Object ids: %s' % object_ids)
        return object_ids

    def fetch_stage(self, harvest_object):
        log.debug('In IotaHarvester fetch_stage (%s)' % harvest_object.guid)
        try:
            harvest_object.content = self._get_datapackage(harvest_object.guid)
            harvest_object.save()
            return True
        except Exception as e:
            msg = 'Unable to get content for indicator - %s - %r'
            self._save_object_error(msg % (harvest_object.guid, e), harvest_object)

    def import_stage(self, harvest_object):
        log.debug('In IotaHarvester import_stage (%s)' % harvest_object.guid)
        log.debug(harvest_object)
        self._set_config(harvest_object)
        content = json.loads(harvest_object.content)
        resources = self._format_resources_to_package_creation(content['resources'])
        groups = self.config.get('groups', [])
        dataset_id = hashlib.sha1(harvest_object.guid).hexdigest()
        dataset = {
          'id': dataset_id,
          'title': content['title'],
          'notes': content['description'],
          'author': content['author'],
          'author_email': content['author_email'],
          'resources': resources,
          'tags': content['keywords'],
          'groups': groups,
          'extras': {
              'source_url': harvest_object.guid
          }
        }

        log.debug('Dataset dict: %s' % dataset)

        return self._create_or_update_package(dataset, harvest_object)

    def _get_related_packages(self, base_url):
        try:
            datapackage = self._get_datapackage(base_url)
            content = json.loads(datapackage)
            return content.get('related', [])
        except TypeError:
            raise Exception(datapackage)

    def _get_datapackage(self, base_url):
        url = base_url + '/datapackage.json'
        return urllib2.urlopen(url).read()

    def _format_resources_to_package_creation(self, resources):
        def convert(resource):
            return {
                     'name': resource['name'],
                     'url': resource['path'],
                     'format': resource['format']
                   }

        return map(convert, resources)

    def _set_config(self, harvest_job):
        config_str = harvest_job.source.config or '{}'
        self.config = json.loads(config_str)
        self.config.setdefault('api_version', self.DEFAULT_API_VERSION)
        log.debug('Using config: %r', self.config)
