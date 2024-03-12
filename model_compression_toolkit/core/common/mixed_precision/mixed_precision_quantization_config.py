# Copyright 2021 Sony Semiconductor Israel, Inc. All rights reserved.
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

from typing import List, Callable

from model_compression_toolkit.core.common.mixed_precision.distance_weighting import MpDistanceWeighting
from model_compression_toolkit.core.common.mixed_precision.kpi_tools.kpi import KPI


class MixedPrecisionQuantizationConfig:

    def __init__(self,
                 target_kpi: KPI = None,
                 compute_distance_fn: Callable = None,
                 distance_weighting_method: MpDistanceWeighting = MpDistanceWeighting.AVG,
                 num_of_images: int = 32,
                 configuration_overwrite: List[int] = None,
                 num_interest_points_factor: float = 1.0,
                 use_hessian_based_scores: bool = False,
                 norm_scores: bool = True,
                 refine_mp_solution: bool = True,
                 metric_normalization_threshold: float = 1e10):
        """
        Class with mixed precision parameters to quantize the input model.

        Args:
            target_kpi (KPI): KPI to constraint the search of the mixed-precision configuration for the model.
            compute_distance_fn (Callable): Function to compute a distance between two tensors. If None, using pre-defined distance methods based on the layer type for each layer.
            distance_weighting_method (MpDistanceWeighting): MpDistanceWeighting enum value that provides a function to use when weighting the distances among different layers when computing the sensitivity metric.
            num_of_images (int): Number of images to use to evaluate the sensitivity of a mixed-precision model comparing to the float model.
            configuration_overwrite (List[int]): A list of integers that enables overwrite of mixed precision with a predefined one.
            num_interest_points_factor (float): A multiplication factor between zero and one (represents percentage) to reduce the number of interest points used to calculate the distance metric.
            use_hessian_based_scores (bool): Whether to use Hessian-based scores for weighted average distance metric computation.
            norm_scores (bool): Whether to normalize the returned scores for the weighted distance metric (to get values between 0 and 1).
            refine_mp_solution (bool): Whether to try to improve the final mixed-precision configuration using a greedy algorithm that searches layers to increase their bit-width, or not.
            metric_normalization_threshold (float): A threshold for checking the mixed precision distance metric values, In case of values larger than this threshold, the metric will be scaled to prevent numerical issues.

        """

        self.target_kpi = target_kpi
        self.compute_distance_fn = compute_distance_fn
        self.distance_weighting_method = distance_weighting_method
        self.num_of_images = num_of_images
        self.configuration_overwrite = configuration_overwrite
        self.refine_mp_solution = refine_mp_solution

        assert 0.0 < num_interest_points_factor <= 1.0, "num_interest_points_factor should represent a percentage of " \
                                                        "the base set of interest points that are required to be " \
                                                        "used for mixed-precision metric evaluation, " \
                                                        "thus, it should be between 0 to 1"
        self.num_interest_points_factor = num_interest_points_factor

        self.use_hessian_based_scores = use_hessian_based_scores
        self.norm_scores = norm_scores

        self.metric_normalization_threshold = metric_normalization_threshold

    def set_target_kpi(self, target_kpi: KPI):
        """
        Setting target KPI in mixed precision config.

        Args:
            target_kpi: A target KPI to set.

        """

        self.target_kpi = target_kpi
