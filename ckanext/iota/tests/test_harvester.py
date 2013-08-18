# -*- coding: utf-8 -*-
import unittest
import mock
import hashlib
import json
import urllib2

import ckanext.harvest.model
import ckanext.iota.iotaharvester

HarvestJob = ckanext.harvest.model.HarvestJob
HarvestObject = ckanext.harvest.model.HarvestObject
IotaHarvester = ckanext.iota.iotaharvester.IotaHarvester
Mock = mock.Mock


class TestIota(unittest.TestCase):
    def test_gather_stage(self):
        job = Mock(spec=HarvestJob)
        job.source.url = 'http://iota_source//'
        with mock.patch('ckanext.iota.iotaharvester.HarvestObject') as harvest_object:
            instance = harvest_object.return_value
            guid = hashlib.sha1(job.source.url.rstrip('/')).hexdigest()

            result = IotaHarvester().gather_stage(job)

            instance.save.assert_called()
            harvest_object.assert_called_with(guid = guid, job = job)
            assert result == [instance.id], result

    def test_fetch_stage(self):
        harvest_object = Mock(spec=HarvestObject)
        harvest_object.source.url = 'http://iota_source//'

        with mock.patch('urllib2.urlopen') as mock_urlopen:
            content = {'some': 'json'}
            mock_urlopen.return_value.read.return_value = json.dumps(content)

            result = IotaHarvester().fetch_stage(harvest_object)

            mock_urlopen.assert_called_with(harvest_object.source.url + '/datapackage.json')
            harvest_object.save.assert_called()
            assert harvest_object.content == json.dumps(content), harvest_object.content
            assert result is True, result

    def test_get_datapackage_returns_empty_dict_on_error(self):
        with mock.patch('urllib2.urlopen') as mock_urlopen:
            mock_urlopen.side_effect = urllib2.URLError('Some URL Error ocurred')

            result = IotaHarvester()._get_datapackage('some_url')

            assert json.loads(result) == {}, result

    def test_import_stage(self):
        content = {
            'title': 'Joao Pessoa',
            'description': 'Some development indicators',
            'resources': [
                {
                    'name': 'Variáveis',
                    'path': 'http://iota_source/variaveis.csv',
                    'format': 'csv'
                },
                {
                    'name': 'Indicadores',
                    'path': 'http://iota_source/indicadores.csv',
                    'format': 'csv'
                }
            ],
            'keywords': [
                'Brasil',
                'PB',
                'Joao Pessoa'
            ]
        }
        harvest_object = Mock(spec=HarvestObject)
        harvest_object.guid = 'object_guid'
        harvest_object.content = json.dumps(content)
        iota = IotaHarvester()
        iota._create_or_update_package = Mock()
        iota._create_or_update_package.return_value = True

        result = iota.import_stage(harvest_object)

        dataset_dict = {
            'id': harvest_object.guid,
            'title': content['title'],
            'notes': content['description'],
            'resources': [
                {
                    'name': 'Variáveis',
                    'url': content['resources'][0]['path'],
                    'format': 'CSV'
                },
                {
                    'name': 'Indicadores',
                    'url': content['resources'][1]['path'],
                    'format': 'CSV'
                },
            ],
            'tags': [
                'Brasil',
                'PB',
                'Joao Pessoa'
            ]
        }
        iota._create_or_update_package.assert_called_with(dataset_dict,
                harvest_object)
        assert result is True, result
