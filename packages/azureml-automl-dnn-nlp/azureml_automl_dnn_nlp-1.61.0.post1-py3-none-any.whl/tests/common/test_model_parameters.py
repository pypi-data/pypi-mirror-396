import unittest

from azureml.automl.core.shared.constants import Tasks
from azureml.automl.dnn.nlp.common.model_parameters import (
    DEFAULT_NLP_PARAMETERS,
    DefaultParameterFactory
)


class TestDefaultParameters(unittest.TestCase):
    """Test NLP default parameter factory logic."""
    def test_task_specific_default_parameters(self):
        for task in DefaultParameterFactory.TASK_TO_PARAM_MAPPING:
            expected = DEFAULT_NLP_PARAMETERS.copy()
            expected.update(DefaultParameterFactory.TASK_TO_PARAM_MAPPING[task])
            self.assertEqual(expected, DefaultParameterFactory.get(task_type=task, model_name=None))

    def test_task_model_pairwise_default_parameters(self):
        for task_model_tuple in DefaultParameterFactory.TASK_MODEL_TO_PARAM_MAPPING:
            expected = DEFAULT_NLP_PARAMETERS.copy()
            expected.update(DefaultParameterFactory.TASK_TO_PARAM_MAPPING[task_model_tuple[0]])
            expected.update(DefaultParameterFactory.MODEL_TO_PARAM_MAPPING.get(task_model_tuple[1], {}))
            expected.update(DefaultParameterFactory.TASK_MODEL_TO_PARAM_MAPPING[task_model_tuple])
            self.assertEqual(
                expected, DefaultParameterFactory.get(task_type=task_model_tuple[0], model_name=task_model_tuple[1])
            )

    def test_model_specific_default_parameters(self):
        for model in DefaultParameterFactory.MODEL_TO_PARAM_MAPPING:
            expected = DEFAULT_NLP_PARAMETERS.copy()
            expected.update(DefaultParameterFactory.TASK_TO_PARAM_MAPPING[Tasks.TEXT_CLASSIFICATION])
            expected.update(DefaultParameterFactory.MODEL_TO_PARAM_MAPPING[model])
            expected.update(DefaultParameterFactory.TASK_MODEL_TO_PARAM_MAPPING.get(
                (Tasks.TEXT_CLASSIFICATION, model), {}))
            self.assertEqual(
                expected, DefaultParameterFactory.get(task_type=Tasks.TEXT_CLASSIFICATION, model_name=model)
            )
