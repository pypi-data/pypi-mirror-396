"""Tests for YAML configuration and CLI functionality."""

import os
import json
import tempfile
import shutil
import pytest
from pathlib import Path
from unittest import mock
import sys

import lu
from lu.cli import load_config, remove_recordings, main
from tests.fixtures import Foo


class TestYAMLConfiguration:
    """Tests for record2() function."""

    def test_record_from_yaml_basic(self, tmp_path):
        """Test basic YAML configuration loading and recording."""
        # Create a temporary YAML config file
        yaml_file = tmp_path / "lu.yaml"
        recordings_dir = tmp_path / "recordings"

        yaml_content = f"""targets:
  tests.fixtures.Foo.expensive_method: null
recordings_dir: {recordings_dir}
"""
        yaml_file.write_text(yaml_content)

        # Change to temp directory so lu.yaml is found
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            with lu.record2():
                foo = Foo()
                result = foo.expensive_method()
                assert result is True
                assert foo.call_count == 1

                # Second call should use recording
                result2 = foo.expensive_method()
                assert result2 is True
                assert foo.call_count == 1  # Should not increment

            # Verify recording files were created
            assert recordings_dir.exists()
            recording_files = list(recordings_dir.iterdir())
            assert len(recording_files) > 0

            # Verify manifest was created
            manifest_file = recordings_dir / "recordings.json"
            assert manifest_file.exists()

        finally:
            os.chdir(original_cwd)

    def test_record_from_yaml_with_manifest_file(self, tmp_path):
        """Test YAML configuration with custom manifest file."""
        yaml_file = tmp_path / "lu.yaml"
        recordings_dir = tmp_path / "recordings"
        manifest_file = tmp_path / "custom_manifest.json"

        yaml_content = f"""targets:
  tests.fixtures.Foo.expensive_method: null
recordings_dir: {recordings_dir}
manifest_file: {manifest_file}
"""
        yaml_file.write_text(yaml_content)

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            with lu.record2():
                foo = Foo()
                foo.expensive_method()

            # Verify custom manifest was created
            assert manifest_file.exists()
            assert not (recordings_dir / "recordings.json").exists()

        finally:
            os.chdir(original_cwd)

    def test_record_from_yaml_with_short_hex_length(self, tmp_path):
        """Test YAML configuration with custom short_hex_length."""
        yaml_file = tmp_path / "lu.yaml"
        recordings_dir = tmp_path / "recordings"

        yaml_content = f"""targets:
  tests.fixtures.Foo.expensive_method: null
recordings_dir: {recordings_dir}
short_hex_length: 10
"""
        yaml_file.write_text(yaml_content)

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            with lu.record2():
                foo = Foo()
                foo.expensive_method()

            # Check that recording files exist
            recording_files = list(recordings_dir.glob("*.*"))
            assert len(recording_files) > 0

        finally:
            os.chdir(original_cwd)

    def test_record_from_yaml_missing_file(self, tmp_path):
        """Test that missing YAML file raises FileNotFoundError."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            with pytest.raises(FileNotFoundError, match="lu.yaml"):
                with lu.record2():
                    pass

        finally:
            os.chdir(original_cwd)

    def test_record_from_yaml_no_pyyaml(self, tmp_path, monkeypatch):
        """Test that missing PyYAML raises ImportError."""
        # Mock yaml module as None
        monkeypatch.setattr('lu.yaml', None)

        yaml_file = tmp_path / "lu.yaml"
        yaml_file.write_text("targets: {}\nrecordings_dir: /tmp")

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            with pytest.raises(ImportError, match="PyYAML"):
                with lu.record2():
                    pass

        finally:
            os.chdir(original_cwd)


class TestCLI:
    """Tests for CLI functionality."""

    def test_load_config(self, tmp_path):
        """Test loading configuration from YAML file."""
        yaml_file = tmp_path / "test_config.yaml"
        yaml_content = """targets:
  some.module.function: [arg1]
recordings_dir: /tmp/recordings
"""
        yaml_file.write_text(yaml_content)

        config = load_config(str(yaml_file))

        assert isinstance(config, dict)
        assert 'targets' in config
        assert 'recordings_dir' in config
        assert config['recordings_dir'] == '/tmp/recordings'

    def test_remove_recordings_basic(self, tmp_path):
        """Test removing recordings by pattern."""
        # Set up test environment
        recordings_dir = tmp_path / "recordings"
        recordings_dir.mkdir()

        # Create manifest
        manifest_file = recordings_dir / "recordings.json"
        manifest_data = {
            "abc123": {
                "target": "tests.fixtures.Foo.expensive_method",
                "params": {"x": 1},
                "file": str(recordings_dir / "abc123.zst"),
                "format": "compressed_pickle",
                "compressor": "zstd",
                "exception": False
            },
            "def456": {
                "target": "tests.fixtures.Bar.expensive_method",
                "params": {"y": 2},
                "file": str(recordings_dir / "def456.zst"),
                "format": "compressed_pickle",
                "compressor": "zstd",
                "exception": False
            }
        }

        with open(manifest_file, 'w') as f:
            json.dump(manifest_data, f)

        # Create physical files
        (recordings_dir / "abc123.zst").write_text("dummy data")
        (recordings_dir / "def456.zst").write_text("dummy data")

        # Create YAML config
        yaml_file = tmp_path / "lu.yaml"
        yaml_content = f"""targets:
  tests.fixtures.Foo.expensive_method: null
recordings_dir: {recordings_dir}
"""
        yaml_file.write_text(yaml_content)

        # Remove recordings matching "Foo"
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            remove_recordings("Foo", "lu.yaml")

            # Verify the Foo entry was removed
            with open(manifest_file, 'r') as f:
                updated_manifest = json.load(f)

            assert "abc123" not in updated_manifest
            assert "def456" in updated_manifest

            # Verify physical file was deleted
            assert not (recordings_dir / "abc123.zst").exists()
            assert (recordings_dir / "def456.zst").exists()

        finally:
            os.chdir(original_cwd)

    def test_remove_recordings_by_entry_id(self, tmp_path):
        """Test removing recordings by entry ID pattern."""
        recordings_dir = tmp_path / "recordings"
        recordings_dir.mkdir()

        manifest_file = recordings_dir / "recordings.json"
        manifest_data = {
            "abc123": {
                "target": "tests.fixtures.Foo.expensive_method",
                "params": {},
                "file": str(recordings_dir / "abc123.zst"),
                "format": "compressed_pickle",
                "compressor": "zstd",
                "exception": False
            },
            "xyz789": {
                "target": "tests.fixtures.Bar.expensive_method",
                "params": {},
                "file": str(recordings_dir / "xyz789.zst"),
                "format": "compressed_pickle",
                "compressor": "zstd",
                "exception": False
            }
        }

        with open(manifest_file, 'w') as f:
            json.dump(manifest_data, f)

        (recordings_dir / "abc123.zst").write_text("dummy")
        (recordings_dir / "xyz789.zst").write_text("dummy")

        yaml_file = tmp_path / "lu.yaml"
        yaml_content = f"""recordings_dir: {recordings_dir}
"""
        yaml_file.write_text(yaml_content)

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            remove_recordings("abc", "lu.yaml")

            with open(manifest_file, 'r') as f:
                updated_manifest = json.load(f)

            assert "abc123" not in updated_manifest
            assert "xyz789" in updated_manifest

        finally:
            os.chdir(original_cwd)

    def test_remove_recordings_no_matches(self, tmp_path, capsys):
        """Test removing recordings when no matches are found."""
        recordings_dir = tmp_path / "recordings"
        recordings_dir.mkdir()

        manifest_file = recordings_dir / "recordings.json"
        manifest_data = {
            "abc123": {
                "target": "tests.fixtures.Foo.expensive_method",
                "params": {},
                "file": str(recordings_dir / "abc123.zst"),
                "format": "compressed_pickle",
                "compressor": "zstd",
                "exception": False
            }
        }

        with open(manifest_file, 'w') as f:
            json.dump(manifest_data, f)

        yaml_file = tmp_path / "lu.yaml"
        yaml_content = f"""recordings_dir: {recordings_dir}
"""
        yaml_file.write_text(yaml_content)

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            remove_recordings("nonexistent_pattern", "lu.yaml")

            captured = capsys.readouterr()
            assert "No recordings found" in captured.out

            # Verify manifest unchanged
            with open(manifest_file, 'r') as f:
                unchanged_manifest = json.load(f)
            assert "abc123" in unchanged_manifest

        finally:
            os.chdir(original_cwd)

    def test_cli_main_remove(self, tmp_path, monkeypatch, capsys):
        """Test CLI main function with remove command."""
        recordings_dir = tmp_path / "recordings"
        recordings_dir.mkdir()

        manifest_file = recordings_dir / "recordings.json"
        manifest_data = {
            "test123": {
                "target": "tests.fixtures.Foo.expensive_method",
                "params": {},
                "file": str(recordings_dir / "test123.zst"),
                "format": "compressed_pickle",
                "compressor": "zstd",
                "exception": False
            }
        }

        with open(manifest_file, 'w') as f:
            json.dump(manifest_data, f)

        (recordings_dir / "test123.zst").write_text("dummy")

        yaml_file = tmp_path / "lu.yaml"
        yaml_content = f"""recordings_dir: {recordings_dir}
"""
        yaml_file.write_text(yaml_content)

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            # Mock sys.argv
            monkeypatch.setattr(sys, 'argv', ['lu', 'remove', 'test123'])

            main()

            # Verify removal
            with open(manifest_file, 'r') as f:
                updated_manifest = json.load(f)

            assert "test123" not in updated_manifest
            assert not (recordings_dir / "test123.zst").exists()

        finally:
            os.chdir(original_cwd)

    def test_cli_main_no_command(self, monkeypatch, capsys):
        """Test CLI main function with no command shows help."""
        monkeypatch.setattr(sys, 'argv', ['lu'])

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert 'usage:' in captured.out or 'usage:' in captured.err
