import unittest
import json
import yaml
import os
from unittest.mock import patch
from step_workflow import get_config_from_file
from step_workflow import get_config_from_cli
from step_workflow import execute_steps

class TestStepWorkflow(unittest.TestCase):
    def setUp(self):
        self.json_file = 'test.json'
        self.yaml_file = 'test.yaml'
        self.invalid_format_file = 'test.txt'
        self.nonexistent_file = 'nonexistent.yaml'
        self.empty_file = 'empty.json'
        self.workflow = {'step1': 'value'}

        with open(self.json_file, 'w') as f:
            json.dump({'workflow': self.workflow}, f)

        with open(self.yaml_file, 'w') as f:
            yaml.dump({'workflow': self.workflow}, f)

        with open(self.invalid_format_file, 'w') as f:
            f.write("'workflow': self.workflow")

        # fill empty file
        open(self.empty_file, 'w').close()


    # on close, delete all support files
    def tearDown(self):
        os.remove(self.json_file)
        os.remove(self.yaml_file)
        os.remove(self.invalid_format_file)
        os.remove(self.empty_file)

    # get_config_file
    def test_get_config_from_file_json(self):
        config = get_config_from_file(self.json_file)
        self.assertEqual(config, self.workflow, 'La lettura dei file JSON è sbagliata: quello che leggo non è quello che mi aspetto.')

    def test_get_config_from_file_yaml(self):
        config = get_config_from_file(self.yaml_file)
        self.assertEqual(config, self.workflow, 'La lettura dei file YAML è sbagliata: quello che leggo non è quello che mi aspetto.')

    def test_get_config_from_file_invalid(self):
        with self.assertRaises(SystemExit):
            get_config_from_file(self.invalid_format_file)

    def test_get_config_from_file_nonexistent(self):
        with self.assertRaises(SystemExit):
            get_config_from_file(self.nonexistent_file)

    def test_get_config_from_file_empty(self):
        with self.assertRaises(SystemExit):
            get_config_from_file(self.empty_file)

    # get_config_from_cli
    def test_get_config_from_cli(self):
        input_config = 'step1:param1,param2 step2:param3,param4,param5'
        expected_output = {
            'step1': ['param1', 'param2'],
            'step2': ['param3', 'param4', 'param5']
        }
        self.assertEqual(get_config_from_cli(input_config), expected_output, "Error, test_get_config_from_cli")

    def test_get_config_from_cli_invalid(self):
        input_config = 'stepwrong:param1,param2 step2:param3,param4,param5'
        expected_output = {
            'step1': ['param1', 'param2'],
            'step2': ['param3', 'param4', 'param5']
        }
        self.assertNotEqual(get_config_from_cli(input_config), expected_output, "Error, test_get_config_from_cli_invalid sono uguali")
    
    def test_get_config_from_cli_empty(self):
        input_config = ''
        expected_output = {}
        self.assertEqual(get_config_from_cli(input_config), expected_output, 'Error: test_get_config_from_cli_empty')

    def test_get_config_from_cli_single_param(self):
        input_config = 'step1:param1 step2:param2'
        expected_output = {
            'step1': ['param1'],
            'step2': ['param2']
        }
        self.assertEqual(get_config_from_cli(input_config), expected_output, 'Error: test_get_config_from_cli_single_param')
    
    # test_execute_steps
    @patch('step_workflow.step1', autospec=True)  
    def test_execute_steps_single(self, mock_step):
        # check steps_params_input in valid_steps
        steps_params_input = {
            'step1': ['param1', 'param2']
        }
        execute_steps(steps_params_input)
        mock_step.run.assert_called_once_with(steps_params_input['step1'])
        
    @patch('step_workflow.step2', autospec=True)
    @patch('step_workflow.step1', autospec=True)
    def test_execute_steps_multi(self, mock_step1, mock_step2):
        # check steps_params_input in valid_steps
        steps_params_input = {
            'step1': ['param1', 'param2'],
            'step2': ['param3', 'param4']
        }
        execute_steps(steps_params_input)
        mock_step1.run.assert_called_once_with(steps_params_input['step1'])
        mock_step2.run.assert_called_once_with(steps_params_input['step2'])

    @patch('step_workflow.step2', autospec=True)
    @patch('step_workflow.step1', autospec=True)
    def test_execute_steps_invalid_step(self, mock_step1, mock_step2):
        steps_params_input = {
            'invalid_step': ['param1', 'param2']
        }
        with self.assertRaises(SystemExit):
            execute_steps(steps_params_input)
        mock_step1.run.assert_not_called()
        mock_step2.run.assert_not_called()

    @patch('step_workflow.step1', autospec=True)
    def test_execute_steps_empty(self, mock_step):
        steps_params_input = {}
        with self.assertRaises(SystemExit):
            execute_steps(steps_params_input)
        mock_step.run.assert_not_called()

    
if __name__ == '__main__':
    unittest.main()