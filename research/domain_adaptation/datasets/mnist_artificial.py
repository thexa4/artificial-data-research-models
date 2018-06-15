# Copyright 2017 Google Inc.
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

"""Provides data for the MNIST-Artificial dataset.

"""





import os
# Dependency imports
import tensorflow as tf

from slim.datasets import dataset_utils

slim = tf.contrib.slim

_FILE_PATTERN = 'mnist_artificial_%s.tfrecord'

_SPLITS_TO_SIZES = {'train': 58001, 'valid': 1000, 'test': 9001}

_NUM_CLASSES = 10

_ITEMS_TO_DESCRIPTIONS = {
    'image': 'A [28 x 28 x 1] image.',
    'label': 'A single integer between 0 and 9',
}


def get_split(split_name, dataset_dir, file_pattern=None, reader=None):
  """Gets a dataset tuple with instructions for reading MNIST.

  Args:
    split_name: A train/test split name.
    dataset_dir: The base directory of the dataset sources.

  Returns:
    A `Dataset` namedtuple.

  Raises:
    ValueError: if `split_name` is not a valid train/test split.
  """
  if split_name not in _SPLITS_TO_SIZES:
    raise ValueError('split name %s was not recognized.' % split_name)

  if not file_pattern:
    file_pattern = _FILE_PATTERN
  file_pattern = os.path.join(dataset_dir, file_pattern % split_name)

  # Allowing None in the signature so that dataset_factory can use the default.
  if reader is None:
    reader = tf.TFRecordReader

  keys_to_features = {
      'image/encoded':
          tf.FixedLenFeature((), tf.string, default_value=''),
      'image/format':
          tf.FixedLenFeature((), tf.string, default_value='png'),
      'image/class/label':
          tf.FixedLenFeature(
              [1], tf.int64, default_value=tf.zeros([1], dtype=tf.int64)),
  }

  items_to_handlers = {
      'image': slim.tfexample_decoder.Image(shape=[28, 28, 1], channels=1),
      'label': slim.tfexample_decoder.Tensor('image/class/label', shape=[]),
  }

  decoder = slim.tfexample_decoder.TFExampleDecoder(
      keys_to_features, items_to_handlers)

  samples = _SPLITS_TO_SIZES[split_name]
  folder_name = split_name
  if folder_name == "valid":
    folder_name = "train"
  folder_pattern = os.path.join(dataset_dir, "mnist_artificial_%s_folder" % folder_name)
  folder_samples = len(os.listdir(folder_pattern)) * 0.9
  if split_name == "train":
    samples = int(folder_samples * 0.9)
  if split_name == "valid":
    samples = folder_samples - int(folder_samples * 0.9)
  if split_name == "test":
    samples = folder_samples

  labels_to_names = None
  if dataset_utils.has_labels(dataset_dir):
    labels_to_names = dataset_utils.read_label_file(dataset_dir)

  print("Samples: " + str(samples))
  print(os.path.join(dataset_dir, "mnist_artificial_%s.count" % split_name))

  with open(os.path.join(dataset_dir, "mnist_artificial_%s.count" % split_name), 'w') as f:
    f.write(str(samples))
    
  return slim.dataset.Dataset(
      data_sources=file_pattern,
      reader=reader,
      decoder=decoder,
      num_samples=samples,
      num_classes=_NUM_CLASSES,
      items_to_descriptions=_ITEMS_TO_DESCRIPTIONS,
      labels_to_names=labels_to_names)
