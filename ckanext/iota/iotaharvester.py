# -*- coding: utf-8 -*-
import urllib2
import hashlib
import json
import logging
import os.path

import ckanext.harvest.model
import ckanext.harvest.harvesters

log = logging.getLogger(__name__)
HarvestObject = ckanext.harvest.model.HarvestObject
HarvesterBase = ckanext.harvest.harvesters.HarvesterBase


class IotaHarvester(HarvesterBase):
    '''
    A Harvester for Iota instances
    '''

    def info(self):
        return {
            'name': 'iota',
            'title': 'Iota',
            'description': 'Harvests Iota instances'
        }

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
        content = json.loads(harvest_object.content)
        resources = self._format_resources_to_package_creation(content['resources'])
        dataset = {
          'id': harvest_object.guid,
          'title': content['title'],
          'notes': content['description'],
          'author': content['author'],
          'author_email': content['author_email'],
          'resources': resources,
          'tags': content['keywords']
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
