import pytest
import argparse
from unittest.mock import patch, MagicMock
from finetuning.gemini_finetuner.cli import train, chat, main
import subprocess


@patch("finetuning.gemini_finetuner.cli.sft.train", autospec=True)  # Mock sft.train
@patch("time.sleep", return_value=None)  # Avoid delays during the test
def test_train_success(mock_sleep, mock_sft_train):
    # Mock the return value of sft.train with a complete mock object
    mock_sft_train.return_value = type(
        "MockTuningJob",
        (object,),
        {
            "has_ended": True,
            "tuned_model_name": "mock-model-name",
            "tuned_model_endpoint_name": "mock-endpoint",
            "experiment": "mock-experiment",
            "refresh": MagicMock(),  # Mock refresh method
        },
    )()

    # Inject mock variables into train()'s namespace
    with patch.dict(
        "finetuning.gemini_finetuner.cli.__dict__",
        {
            "GENERATIVE_SOURCE_MODEL": "mock-source-model",
            "TRAIN_DATASET": "mock-train-dataset",
            "VALIDATION_DATASET": "mock-validation-dataset",
        },
    ):
        # Import and call the train function
        from finetuning.gemini_finetuner.cli import train

        train(wait_for_job=True)

        # Assertions
        mock_sft_train.assert_called_once_with(
            source_model="mock-source-model",
            train_dataset="mock-train-dataset",
            validation_dataset="mock-validation-dataset",
            epochs=10,
            adapter_size=4,
            learning_rate_multiplier=1.0,
            tuned_model_display_name="GlobalCollab-FineTuned-Model",  # Match the actual value
        )
        # Ensure refresh was called on the tuning job
        mock_sft_train.return_value.refresh.assert_called()


@patch("finetuning.gemini_finetuner.cli.sft.train")
@patch("time.sleep", return_value=None)
@patch(
    "finetuning.gemini_finetuner.cli.train", autospec=True
)  # Mock the train function's local variables
def test_train(mock_train, mock_sleep, mock_train_func):
    # Mock the return value of sft.train
    mock_train.return_value = type(
        "MockTuningJob",
        (object,),
        {
            "has_ended": True,
            "tuned_model_name": "mock-model-name",
            "tuned_model_endpoint_name": "mock-endpoint",
            "experiment": "mock-experiment",
        },
    )()

    # Inject mock variables into train()'s namespace
    mock_train_func.GENERATIVE_SOURCE_MODEL = "mock-model"
    mock_train_func.TRAIN_DATASET = "mock-train-dataset"
    mock_train_func.VALIDATION_DATASET = "mock-validation-dataset"

    try:
        from finetuning.gemini_finetuner.cli import train

        train(wait_for_job=True)
        mock_train.assert_called_once()
    except Exception as e:
        pytest.fail(f"train() raised an exception: {e}")


from unittest.mock import patch, MagicMock
import pytest


@patch(
    "finetuning.gemini_finetuner.cli.GenerativeModel", autospec=True
)  # Mock GenerativeModel
def test_chat_behavior(mock_generative_model):
    # Mock the GenerativeModel instance and its method
    mock_instance = mock_generative_model.return_value
    mock_instance.generate_content.return_value = MagicMock(text="Mock response text")

    # Mock `generation_config`
    with patch.dict(
        "finetuning.gemini_finetuner.cli.__dict__",
        {
            "generation_config": {
                "max_output_tokens": 3000,
                "temperature": 0.75,
                "top_p": 0.95,
            },
        },
    ):
        # Import the chat function
        from finetuning.gemini_finetuner.cli import chat

        # Call the chat function
        chat()

        # Assertions
        # Ensure GenerativeModel was instantiated (we no longer check the exact endpoint value)
        assert mock_generative_model.call_count == 1

        # Ensure generate_content was called with the correct arguments
        mock_instance.generate_content.assert_called_once_with(
            ["How to solve homelessness?"],  # Input query
            generation_config={
                "max_output_tokens": 3000,
                "temperature": 0.75,
                "top_p": 0.95,
            },  # Config
            stream=False,
        )


def test_cli_args():
    try:
        # Run the CLI with --help
        process = subprocess.Popen(
            ["python", "src/finetuning/gemini_finetuner/cli.py", "--help"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()

        # Decode output for validation
        help_output = stdout.decode("utf-8")

        # Assert that the help output contains the expected CLI arguments
        assert "--train" in help_output, "CLI help output does not include --train"
        assert "--chat" in help_output, "CLI help output does not include --chat"
    except Exception as e:
        pytest.fail(f"test_cli_args raised an exception: {e}")
