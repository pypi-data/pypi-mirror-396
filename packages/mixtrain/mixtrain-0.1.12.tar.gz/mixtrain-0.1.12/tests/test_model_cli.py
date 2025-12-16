"""Tests for model CLI commands."""

import pytest
from unittest.mock import Mock, patch
from typer.testing import CliRunner
from mixtrain.model import app

class TestModelCLI:
    """Test model CLI commands."""

    def test_model_update_metadata_success(self, cli_runner, mock_config):
        """Test successful model update (metadata only)."""
        mock_result = {
            "data": {
                "name": "updated-model",
                "description": "Updated description"
            }
        }
        
        with patch("mixtrain.client.MixClient.update_model") as mock_update:
            mock_update.return_value = mock_result
            
            result = cli_runner.invoke(app, [
                "update", "test-model",
                "--name", "updated-model",
                "--description", "Updated description"
            ])
            
            assert result.exit_code == 0
            assert "✓" in result.stdout
            assert "Successfully updated model 'updated-model'" in result.stdout
            mock_update.assert_called_once_with(
                model_name="test-model",
                name="updated-model",
                description="Updated description",
                file_path=None
            )

    def test_model_update_file_success(self, cli_runner, mock_config, tmp_path):
        """Test successful model update with file."""
        # Create dummy file
        model_file = tmp_path / "model.py"
        model_file.write_text("print('hello')")
        
        mock_result = {
            "data": {
                "name": "test-model",
                "description": "Test model"
            }
        }
        
        with patch("mixtrain.client.MixClient.update_model") as mock_update:
            mock_update.return_value = mock_result
            
            result = cli_runner.invoke(app, [
                "update", "test-model",
                "--file", str(model_file)
            ])
            
            assert result.exit_code == 0
            assert "✓" in result.stdout
            assert "Successfully updated model 'test-model'" in result.stdout
            assert "Uploaded new model file" in result.stdout
            
            mock_update.assert_called_once_with(
                model_name="test-model",
                name=None,
                description=None,
                file_path=str(model_file)
            )

    def test_model_update_file_not_found(self, cli_runner, mock_config):
        """Test model update with non-existent file."""
        result = cli_runner.invoke(app, [
            "update", "test-model",
            "--file", "/nonexistent/model.py"
        ])
        
        assert result.exit_code == 1
        assert "File not found" in result.stdout

    def test_model_update_api_error(self, cli_runner, mock_config):
        """Test model update with API error."""
        with patch("mixtrain.client.MixClient.update_model") as mock_update:
            mock_update.side_effect = Exception("API Error")
            
            result = cli_runner.invoke(app, [
                "update", "test-model",
                "--name", "updated-model"
            ])
            
            assert result.exit_code == 1
            assert "Error:" in result.stdout
            assert "API Error" in result.stdout
