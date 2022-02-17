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

keras = tf.keras
layers = keras.layers


class ShiftNegActivationTest(BaseKerasFeatureNetworkTest):
    def __init__(self, unit_test, linear_op_to_test, activation_op_to_test, use_pad_layer=False, input_shape=(8, 8, 3)):
        assert type(linear_op_to_test) in [layers.Conv2D, layers.Dense, layers.DepthwiseConv2D]
        self.linear_op_to_test = linear_op_to_test
        self.activation_op_to_test = activation_op_to_test
        self.use_pad_layer = use_pad_layer
        super().__init__(unit_test, input_shape=input_shape)

    def get_quantization_config(self):
        return mct.QuantizationConfig(mct.QuantizationErrorMethod.MSE, mct.QuantizationErrorMethod.MSE,
                                      mct.QuantizationMethod.POWER_OF_TWO, mct.QuantizationMethod.POWER_OF_TWO, 16, 16,
                                      False, False, True, shift_negative_activation_correction=True,
                                      shift_negative_ratio=np.inf)

    def create_networks(self):
        inputs = layers.Input(shape=self.get_input_shapes()[0][1:])
        x = self.activation_op_to_test(inputs)
        if self.use_pad_layer:
            x = layers.ZeroPadding2D(((3, 4), (5, 6)))(x)
        outputs = self.linear_op_to_test(x)
        return keras.Model(inputs=inputs, outputs=outputs)

    def compare(self, quantized_model, float_model, input_x=None, quantization_info=None):
        self.unit_test.assertTrue(float_model.output.shape.as_list() == quantized_model.output.shape.as_list(),
                                  msg=f'Outputs shape mismatch: {float_model.output.shape} != {quantized_model.output.shape}')
        if isinstance(self.activation_op_to_test, tf.keras.layers.PReLU):
            _, w, b = float_model.get_weights()
        else:
            w, b = float_model.get_weights()
        linear_op_index = 3 + (4 if self.use_pad_layer else 3)
        linear_op_index = linear_op_index + int(self.linear_op_to_test.get_config().get('padding') == 'same')
        q_w, q_b = quantized_model.layers[linear_op_index].weights[0].numpy(), \
                   quantized_model.layers[linear_op_index].weights[1].numpy()
        # Take the ACTUAL value the activations were shifted by, from the Add layer the substitution needs to insert
        add_layer_index = 4  # should be always the fourth layer (input, fq, swish, add)
        shift_nl_out = quantized_model.layers[add_layer_index].constants[1].item()
        if isinstance(self.linear_op_to_test, layers.DepthwiseConv2D):
            self.unit_test.assertTrue(np.allclose(b - q_b, shift_nl_out * np.sum(w, axis=(0, 1)).flatten()))
        elif isinstance(self.linear_op_to_test, layers.Conv2D):
            self.unit_test.assertTrue(np.allclose(b - q_b, shift_nl_out * np.sum(w, axis=(0, 1, 2))))
        elif isinstance(self.linear_op_to_test, layers.Dense):
            self.unit_test.assertTrue(np.allclose(b - q_b, shift_nl_out * np.sum(w, axis=(0))))
        else:
            raise NotImplementedError

