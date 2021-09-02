# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from tensorflow import keras

import data_utils
import trainer

model: Optional[keras.Model] = None


def predict(model: keras.Model, inputs: Dict[str, np.ndarray]) -> pd.DataFrame:
    normalized_inputs = data_utils.with_fixed_time_steps(inputs)

    # Our model always expects a batch prediction, so we create a batch with
    # a single prediction request.
    #   {input: [time_steps, 1]} --> {input: [1, time_steps, 1]}
    inputs_batch = {
        name: np.reshape(values, (1, len(values), 1))
        for name, values in normalized_inputs.to_dict("list").items()
    }

    predictions = model.predict(inputs_batch)
    return normalized_inputs[trainer.PADDING :].assign(
        is_precipitation=predictions["is_precipitation"][0]
    )


def run(model_dir: str, inputs: Dict[str, List[float]]) -> Dict[str, np.ndarray]:
    # Cache the model so it only has to be loaded once per runtime.
    global model
    if model is None:
        model = keras.models.load_model(model_dir)

    return predict(model, inputs).to_dict("list")
