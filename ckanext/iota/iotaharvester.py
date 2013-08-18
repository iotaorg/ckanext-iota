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

        base_url = harvest_job.source.url.rstrip('/')
        guid = hashlib.sha1(base_url).hexdigest()

        obj = HarvestObject(guid = guid, job = harvest_job)
        log.debug(obj)
        obj.save()

        log.debug('Object ids: [%s]' % obj.id)
        return [obj.id]

    def fetch_stage(self, harvest_object):
        log.debug('In IotaHarvester fetch_stage (%s)' % harvest_object.guid)
        url = harvest_object.source.url
        harvest_object.content = self._get_datapackage(url)
        harvest_object.save()
        return True

    def import_stage(self, harvest_object):
        log.debug('In IotaHarvester import_stage (%s)' % harvest_object.guid)
        log.debug(harvest_object)
        content = json.loads(harvest_object.content)
        resources = self._format_resources_to_package_creation(content['resources'])
        dataset = {
          'id': harvest_object.guid,
          'title': content['title'],
          'notes': content['description'],
          'resources': resources,
          'tags': content['keywords']
        }

        log.debug('Dataset dict: %s' % dataset)
        return self._create_or_update_package(dataset, harvest_object)

    def _get_datapackage(self, base_url):
        try:
            url = base_url + '/datapackage.json'
            return urllib2.urlopen(url).read()
        except urllib2.URLError:
            return '{}'

    def _format_resources_to_package_creation(self, resources):
        def convert(resource):
            return {
                     'name': resource['name'],
                     'url': resource['path'],
                     'format': resource['format']
                   }

        return map(convert, resources)
