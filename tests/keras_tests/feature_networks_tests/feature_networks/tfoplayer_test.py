# Copyright 2021 Sony Semiconductors Israel, Inc. All rights reserved.
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
# ==============================================================================


from tests.common_tests.base_feature_test import BaseFeatureNetworkTest
import model_compression_toolkit as mct
import tensorflow as tf
from tests.keras_tests.feature_networks_tests.base_keras_feature_test import BaseKerasFeatureNetworkTest
import numpy as np
from tests.common_tests.helpers.tensors_compare import cosine_similarity
from model_compression_toolkit.common.quantization.quantization_config import DEFAULTCONFIG

keras = tf.keras
layers = keras.layers


class TFOpLayerTest(BaseKerasFeatureNetworkTest):
    def __init__(self, unit_test):
        super().__init__(unit_test, input_shape=(320,320,3))

    def create_networks(self):
        model_path = '/data/projects/swat/network_database/ModelZoo/Float-Keras-Models/SSD_MobileNetV2_FPNLite/SSD_MobileNet_V2_FPNLite_320x320_no_pp.h5'
        return tf.keras.models.load_model(model_path, compile=False)


    def compare(self, quantized_model, float_model, input_x=None, quantization_info=None):
        pass
