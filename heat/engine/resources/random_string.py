# vim: tabstop=4 shiftwidth=4 softtabstop=4

#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from heat.db import api as db_api
from heat.engine import resource
from heat.engine import properties

import random
import string


class RandomString(resource.Resource):
    '''
    A resource which generates a random string.

    This is useful for configuring passwords and secrets on services.
    '''
    properties_schema = {
        'length': properties.Schema(
            properties.INTEGER,
            _('Length of the string to generate.'),
            default=32,
            constraints=[properties.Range(1, 512)]),
        'sequence': properties.Schema(
            properties.STRING,
            _('Sequence of characters to build the random string from.'),
            default='lettersdigits',
            constraints=[properties.AllowedValues((
                'lettersdigits', 'letters', 'lowercase', 'uppercase', 'digits',
                'hexdigits', 'octdigits'))]),
        'salt': properties.Schema(
            properties.STRING,
            _('Value which can be set or changed on stack update to trigger '
              'the resource for replacement with a new random string . '
              'The salt value itself is ignored by the random generator.'))
    }

    attributes_schema = {
        'value': _('The random string generated by this resource'),
    }

    _sequences = {
        'lettersdigits': string.ascii_letters + string.digits,
        'letters': string.ascii_letters,
        'lowercase': string.ascii_lowercase,
        'uppercase': string.ascii_uppercase,
        'digits': string.digits,
        'hexdigits': string.digits + 'ABCDEF',
        'octdigits': string.octdigits
    }

    @staticmethod
    def _generate_random_string(sequence, length):
        rand = random.SystemRandom()
        return ''.join(rand.choice(sequence) for x in xrange(length))

    def handle_create(self):
        length = self.properties.get('length')
        sequence = self._sequences[self.properties.get('sequence')]
        random_string = self._generate_random_string(sequence, length)
        db_api.resource_data_set(self, 'value', random_string, redact=True)

    def _resolve_attribute(self, name):
        if name == 'value':
            return db_api.resource_data_get(self, 'value')


def resource_mapping():
    return {
        'OS::Heat::RandomString': RandomString,
    }
