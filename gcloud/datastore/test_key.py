# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest2


class TestKey(unittest2.TestCase):

    _DEFAULT_DATASET = 'DATASET'

    def setUp(self):

        from gcloud.datastore import _implicit_environ
        self._replaced_dataset_id = _implicit_environ.DATASET_ID
        _implicit_environ.DATASET_ID = None

    def tearDown(self):
        from gcloud.datastore import _implicit_environ
        _implicit_environ.DATASET_ID = self._replaced_dataset_id

    def _getTargetClass(self):
        from gcloud.datastore.key import Key
        return Key

    def _makeOne(self, *args, **kwargs):
        return self._getTargetClass()(*args, **kwargs)

    def _monkeyDatasetID(self, dataset_id=_DEFAULT_DATASET):
        from gcloud._testing import _Monkey
        from gcloud.datastore import _implicit_environ
        return _Monkey(_implicit_environ, DATASET_ID=dataset_id)

    def test_ctor_empty(self):
        self.assertRaises(ValueError, self._makeOne)

    def test_ctor_no_dataset_id(self):
        klass = self._getTargetClass()
        with self._monkeyDatasetID(None):
            self.assertRaises(ValueError, klass, 'KIND')

    def test_ctor_w_implicit_dataset_id(self):
        _DATASET = 'DATASET'
        _KIND = 'KIND'
        with self._monkeyDatasetID(_DATASET):
            key = self._makeOne(_KIND)
        self.assertEqual(key.dataset_id, _DATASET)
        self.assertEqual(key.namespace, None)
        self.assertEqual(key.kind, _KIND)
        self.assertEqual(key.path, [{'kind': _KIND}])

    def test_ctor_w_implicit_dataset_id_empty_path(self):
        _DATASET = 'DATASET'
        self.assertRaises(ValueError, self._makeOne, dataset_id=_DATASET)

    def test_ctor_parent(self):
        _PARENT_KIND = 'KIND1'
        _PARENT_ID = 1234
        _PARENT_DATASET = 'DATASET-ALT'
        _PARENT_NAMESPACE = 'NAMESPACE'
        _CHILD_KIND = 'KIND2'
        _CHILD_ID = 2345
        _PATH = [
            {'kind': _PARENT_KIND, 'id': _PARENT_ID},
            {'kind': _CHILD_KIND, 'id': _CHILD_ID},
        ]
        parent_key = self._makeOne(_PARENT_KIND, _PARENT_ID,
                                   dataset_id=_PARENT_DATASET,
                                   namespace=_PARENT_NAMESPACE)
        key = self._makeOne(_CHILD_KIND, _CHILD_ID, parent=parent_key)
        self.assertEqual(key.dataset_id, parent_key.dataset_id)
        self.assertEqual(key.namespace, parent_key.namespace)
        self.assertEqual(key.kind, _CHILD_KIND)
        self.assertEqual(key.path, _PATH)
        self.assertTrue(key.parent is parent_key)

    def test_ctor_partial_parent(self):
        parent_key = self._makeOne('KIND', dataset_id=self._DEFAULT_DATASET)
        with self.assertRaises(ValueError):
            self._makeOne('KIND2', 1234, parent=parent_key)

    def test_ctor_parent_bad_type(self):
        with self.assertRaises(AttributeError):
            self._makeOne('KIND2', 1234, parent=('KIND1', 1234),
                          dataset_id=self._DEFAULT_DATASET)

    def test_ctor_parent_bad_namespace(self):
        parent_key = self._makeOne('KIND', 1234, namespace='FOO',
                                   dataset_id=self._DEFAULT_DATASET)
        with self.assertRaises(ValueError):
            self._makeOne('KIND2', 1234, namespace='BAR', parent=parent_key,
                          dataset_id=self._DEFAULT_DATASET)

    def test_ctor_parent_bad_dataset_id(self):
        parent_key = self._makeOne('KIND', 1234, dataset_id='FOO')
        with self.assertRaises(ValueError):
            self._makeOne('KIND2', 1234, parent=parent_key,
                          dataset_id='BAR')

    def test_ctor_parent_empty_path(self):
        parent_key = self._makeOne('KIND', 1234,
                                   dataset_id=self._DEFAULT_DATASET)
        with self.assertRaises(ValueError):
            self._makeOne(parent=parent_key)

    def test_ctor_explicit(self):
        _DATASET = 'DATASET-ALT'
        _NAMESPACE = 'NAMESPACE'
        _KIND = 'KIND'
        _ID = 1234
        _PATH = [{'kind': _KIND, 'id': _ID}]
        key = self._makeOne(_KIND, _ID, namespace=_NAMESPACE,
                            dataset_id=_DATASET)
        self.assertEqual(key.dataset_id, _DATASET)
        self.assertEqual(key.namespace, _NAMESPACE)
        self.assertEqual(key.kind, _KIND)
        self.assertEqual(key.path, _PATH)

    def test_ctor_bad_kind(self):
        self.assertRaises(ValueError, self._makeOne, object(),
                          dataset_id=self._DEFAULT_DATASET)

    def test_ctor_bad_id_or_name(self):
        self.assertRaises(ValueError, self._makeOne, 'KIND', object(),
                          dataset_id=self._DEFAULT_DATASET)
        self.assertRaises(ValueError, self._makeOne, 'KIND', None,
                          dataset_id=self._DEFAULT_DATASET)
        self.assertRaises(ValueError, self._makeOne, 'KIND', 10, 'KIND2', None,
                          dataset_id=self._DEFAULT_DATASET)

    def test__clone(self):
        _DATASET = 'DATASET-ALT'
        _NAMESPACE = 'NAMESPACE'
        _KIND = 'KIND'
        _ID = 1234
        _PATH = [{'kind': _KIND, 'id': _ID}]
        key = self._makeOne(_KIND, _ID, namespace=_NAMESPACE,
                            dataset_id=_DATASET)
        clone = key._clone()
        self.assertEqual(clone.dataset_id, _DATASET)
        self.assertEqual(clone.namespace, _NAMESPACE)
        self.assertEqual(clone.kind, _KIND)
        self.assertEqual(clone.path, _PATH)

    def test_completed_key_on_partial_w_id(self):
        key = self._makeOne('KIND', dataset_id=self._DEFAULT_DATASET)
        _ID = 1234
        new_key = key.completed_key(_ID)
        self.assertFalse(key is new_key)
        self.assertEqual(new_key.id, _ID)
        self.assertEqual(new_key.name, None)

    def test_completed_key_on_partial_w_name(self):
        key = self._makeOne('KIND', dataset_id=self._DEFAULT_DATASET)
        _NAME = 'NAME'
        new_key = key.completed_key(_NAME)
        self.assertFalse(key is new_key)
        self.assertEqual(new_key.id, None)
        self.assertEqual(new_key.name, _NAME)

    def test_completed_key_on_partial_w_invalid(self):
        key = self._makeOne('KIND', dataset_id=self._DEFAULT_DATASET)
        self.assertRaises(ValueError, key.completed_key, object())

    def test_completed_key_on_complete(self):
        key = self._makeOne('KIND', 1234, dataset_id=self._DEFAULT_DATASET)
        self.assertRaises(ValueError, key.completed_key, 5678)

    def test_to_protobuf_defaults(self):
        from gcloud.datastore._datastore_v1_pb2 import Key as KeyPB
        _KIND = 'KIND'
        key = self._makeOne(_KIND, dataset_id=self._DEFAULT_DATASET)
        pb = key.to_protobuf()
        self.assertTrue(isinstance(pb, KeyPB))

        # Check partition ID.
        self.assertEqual(pb.partition_id.dataset_id, self._DEFAULT_DATASET)
        self.assertEqual(pb.partition_id.namespace, '')
        self.assertFalse(pb.partition_id.HasField('namespace'))

        # Check the element PB matches the partial key and kind.
        elem, = list(pb.path_element)
        self.assertEqual(elem.kind, _KIND)
        self.assertEqual(elem.name, '')
        self.assertFalse(elem.HasField('name'))
        self.assertEqual(elem.id, 0)
        self.assertFalse(elem.HasField('id'))

    def test_to_protobuf_w_explicit_dataset_id(self):
        _DATASET = 'DATASET-ALT'
        key = self._makeOne('KIND', dataset_id=_DATASET)
        pb = key.to_protobuf()
        self.assertEqual(pb.partition_id.dataset_id, _DATASET)

    def test_to_protobuf_w_explicit_namespace(self):
        _NAMESPACE = 'NAMESPACE'
        key = self._makeOne('KIND', namespace=_NAMESPACE,
                            dataset_id=self._DEFAULT_DATASET)
        pb = key.to_protobuf()
        self.assertEqual(pb.partition_id.namespace, _NAMESPACE)

    def test_to_protobuf_w_explicit_path(self):
        _PARENT = 'PARENT'
        _CHILD = 'CHILD'
        _ID = 1234
        _NAME = 'NAME'
        key = self._makeOne(_PARENT, _NAME, _CHILD, _ID,
                            dataset_id=self._DEFAULT_DATASET)
        pb = key.to_protobuf()
        elems = list(pb.path_element)
        self.assertEqual(len(elems), 2)
        self.assertEqual(elems[0].kind, _PARENT)
        self.assertEqual(elems[0].name, _NAME)
        self.assertEqual(elems[1].kind, _CHILD)
        self.assertEqual(elems[1].id, _ID)

    def test_to_protobuf_w_no_kind(self):
        key = self._makeOne('KIND', dataset_id=self._DEFAULT_DATASET)
        # Force the 'kind' to be unset. Maybe `to_protobuf` should fail
        # on this? The backend certainly will.
        key._path[-1].pop('kind')
        pb = key.to_protobuf()
        self.assertFalse(pb.path_element[0].HasField('kind'))

    def test_is_partial_no_name_or_id(self):
        key = self._makeOne('KIND', dataset_id=self._DEFAULT_DATASET)
        self.assertTrue(key.is_partial)

    def test_is_partial_w_id(self):
        _ID = 1234
        key = self._makeOne('KIND', _ID, dataset_id=self._DEFAULT_DATASET)
        self.assertFalse(key.is_partial)

    def test_is_partial_w_name(self):
        _NAME = 'NAME'
        key = self._makeOne('KIND', _NAME, dataset_id=self._DEFAULT_DATASET)
        self.assertFalse(key.is_partial)

    def test_id_or_name_no_name_or_id(self):
        key = self._makeOne('KIND', dataset_id=self._DEFAULT_DATASET)
        self.assertEqual(key.id_or_name, None)

    def test_id_or_name_no_name_or_id_child(self):
        key = self._makeOne('KIND1', 1234, 'KIND2',
                            dataset_id=self._DEFAULT_DATASET)
        self.assertEqual(key.id_or_name, None)

    def test_id_or_name_w_id_only(self):
        _ID = 1234
        key = self._makeOne('KIND', _ID, dataset_id=self._DEFAULT_DATASET)
        self.assertEqual(key.id_or_name, _ID)

    def test_id_or_name_w_name_only(self):
        _NAME = 'NAME'
        key = self._makeOne('KIND', _NAME, dataset_id=self._DEFAULT_DATASET)
        self.assertEqual(key.id_or_name, _NAME)

    def test_parent_default(self):
        key = self._makeOne('KIND', dataset_id=self._DEFAULT_DATASET)
        self.assertEqual(key.parent, None)

    def test_parent_explicit_top_level(self):
        key = self._makeOne('KIND', 1234, dataset_id=self._DEFAULT_DATASET)
        self.assertEqual(key.parent, None)

    def test_parent_explicit_nested(self):
        _PARENT_KIND = 'KIND1'
        _PARENT_ID = 1234
        _PARENT_PATH = [{'kind': _PARENT_KIND, 'id': _PARENT_ID}]
        key = self._makeOne(_PARENT_KIND, _PARENT_ID, 'KIND2',
                            dataset_id=self._DEFAULT_DATASET)
        self.assertEqual(key.parent.path, _PARENT_PATH)

    def test_parent_multiple_calls(self):
        _PARENT_KIND = 'KIND1'
        _PARENT_ID = 1234
        _PARENT_PATH = [{'kind': _PARENT_KIND, 'id': _PARENT_ID}]
        key = self._makeOne(_PARENT_KIND, _PARENT_ID, 'KIND2',
                            dataset_id=self._DEFAULT_DATASET)
        parent = key.parent
        self.assertEqual(parent.path, _PARENT_PATH)
        new_parent = key.parent
        self.assertTrue(parent is new_parent)
