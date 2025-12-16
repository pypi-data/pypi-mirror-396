"""Tests for workflow CLI commands."""

import pytest
from unittest.mock import Mock, patch
from typer.testing import CliRunner
from mixtrain.cli import app

class TestWorkflowCLI:
    """Test workflow CLI commands."""

    def test_workflow_update_metadata_success(self, cli_runner, mock_config):
        """Test successful workflow update (metadata only)."""
        mock_result = {
            "data": {
                "name": "updated-workflow",
                "description": "Updated description"
            }
        }
        
        with patch("mixtrain.client.MixClient.update_workflow") as mock_update:
            mock_update.return_value = mock_result
            
            result = cli_runner.invoke(app, [
                "workflow", "update", "test-workflow",
                "--name", "updated-workflow",
                "--description", "Updated description"
            ])
            
            assert result.exit_code == 0
            assert "✓" in result.stdout
            assert "Successfully updated workflow 'updated-workflow'" in result.stdout
            mock_update.assert_called_once_with(
                workflow_name="test-workflow",
                name="updated-workflow",
                description="Updated description",
                workflow_file=None,
                src_files=None
            )

    def test_workflow_update_files_success(self, cli_runner, mock_config, tmp_path):
        """Test successful workflow update with files."""
        # Create dummy files
        workflow_file = tmp_path / "workflow.py"
        workflow_file.write_text("print('hello')")
        src_file = tmp_path / "utils.py"
        src_file.write_text("def foo(): pass")
        
        mock_result = {
            "data": {
                "name": "test-workflow",
                "description": "Test workflow"
            }
        }
        
        with patch("mixtrain.client.MixClient.update_workflow") as mock_update:
            mock_update.return_value = mock_result
            
            result = cli_runner.invoke(app, [
                "workflow", "update", "test-workflow",
                "--file", str(workflow_file),
                "--src", str(src_file)
            ])
            
            assert result.exit_code == 0
            assert "✓" in result.stdout
            assert "Successfully updated workflow 'test-workflow'" in result.stdout
            assert "Uploaded new workflow file" in result.stdout
            assert "Uploaded 1 additional source file(s)" in result.stdout
            
            mock_update.assert_called_once_with(
                workflow_name="test-workflow",
                name=None,
                description=None,
                workflow_file=str(workflow_file),
                src_files=[str(src_file)]
            )

    def test_workflow_update_file_not_found(self, cli_runner, mock_config):
        """Test workflow update with non-existent file."""
        result = cli_runner.invoke(app, [
            "workflow", "update", "test-workflow",
            "--file", "/nonexistent/file.py"
        ])
        
        assert result.exit_code == 1
        assert "Workflow file not found" in result.stdout

    def test_workflow_update_src_file_not_found(self, cli_runner, mock_config, tmp_path):
        """Test workflow update with non-existent source file."""
        workflow_file = tmp_path / "workflow.py"
        workflow_file.write_text("print('hello')")
        
        result = cli_runner.invoke(app, [
            "workflow", "update", "test-workflow",
            "--file", str(workflow_file),
            "--src", "/nonexistent/utils.py"
        ])
        
        assert result.exit_code == 1
        assert "Source file not found" in result.stdout

    def test_workflow_update_api_error(self, cli_runner, mock_config):
        """Test workflow update with API error."""
        with patch("mixtrain.client.MixClient.update_workflow") as mock_update:
            mock_update.side_effect = Exception("API Error")
            
            result = cli_runner.invoke(app, [
                "workflow", "update", "test-workflow",
                "--name", "updated-workflow"
            ])
            
            assert result.exit_code == 1
            assert "Error:" in result.stdout
            assert "API Error" in result.stdout
