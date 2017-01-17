# Copyright 2016 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import shutil
from mock import call, Mock, patch
import test_utils
import ceph
from tempfile import mkdtemp
import get_bcache_stats

test_stats = {
    'bypassed': '128G\n',
    'cache_bypass_hits': '1132623\n',
    'cache_bypass_misses': '0\n',
    'cache_hit_ratio': '64\n',
    'cache_hits': '12177090\n',
    'cache_miss_collisions': '7091\n',
    'cache_misses': '6717011\n',
    'cache_readaheads': '0\n',
    }

tmpdir = 'bcache-stats-test.'
bcachefs = 'abcde'

class GetBcacheStatsTestCase(test_utils.CharmTestCase):
    def setUp(self):
        self.bcachedir = d = mkdtemp(prefix=tmpdir)
        for n in ['register', 'register_quiet']:
            with open(os.path.join(d, n), 'w') as f:
                f.write('foo')
        self.statsdir = statsd = os.path.join(d, bcachefs)
        os.mkdir(statsd)
        for sub in get_bcache_stats.stats_intervals:
            subdir = os.path.join(statsd, sub)
            os.mkdir(subdir)
            for fn, val in test_stats.items():
                with open(os.path.join(subdir, fn), 'w') as f:
                    f.write(val)
            
    @patch('get_bcache_stats.os')
    def test_get_bcache_fs(self, mock_os):
        mock_os.listdir.return_value = ['register', 'register_quiet', 'abcde']
        bcachedirs = get_bcache_stats.get_bcache_fs()
        assert bcachedirs == ['abcde']
        
    @patch('get_bcache_stats.os')
    def test_get_bcache_fs_nobcache(self, mock_os):
        mock_os.listdir.side_effect = OSError(
            '[Errno 2] No such file or directory:...')
        bcachedirs = get_bcache_stats.get_bcache_fs()
        assert bcachedirs == []
        
    def test_get_stats(self):
        out = get_bcache_stats.get_stats(
            self.statsdir, 'hour')
        assert out.find('bypassed: 128G') != -1

    def tearDown(self):
        shutil.rmtree(self.bcachedir)
        
