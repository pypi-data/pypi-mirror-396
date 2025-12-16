"""
Tests for semiautomatic CLI module.

Tests cover:
- Argument parsing (all options and formats)
- Help and version output
- Command dispatch
- Error handling (missing files, invalid args)
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

from semiautomatic.cli import (
    build_parser,
    main,
    cmd_process_image,
)


# =============================================================================
# build_parser() tests
# =============================================================================

class TestBuildParser:
    """Tests for argument parser construction."""

    def test_parser_has_version(self):
        parser = build_parser()
        # Version action should be present
        assert any(
            action.option_strings == ['--version']
            for action in parser._actions
        )

    def test_parser_has_process_image_subcommand(self):
        parser = build_parser()
        # Check subparsers exist
        assert parser._subparsers is not None

    def test_process_image_size_argument(self):
        parser = build_parser()
        args = parser.parse_args(['process-image', '--size', '1920x1080'])
        assert args.size == '1920x1080'

    def test_process_image_format_argument(self):
        parser = build_parser()
        args = parser.parse_args(['process-image', '--format', 'png'])
        assert args.format == 'png'

    def test_process_image_format_choices(self):
        parser = build_parser()
        # Valid choices should work
        for fmt in ['auto', 'png', 'jpeg']:
            args = parser.parse_args(['process-image', '--format', fmt])
            assert args.format == fmt

    def test_process_image_invalid_format_rejected(self):
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(['process-image', '--format', 'gif'])

    def test_process_image_quality_argument(self):
        parser = build_parser()
        args = parser.parse_args(['process-image', '--quality', '90'])
        assert args.quality == 90

    def test_process_image_quality_default(self):
        parser = build_parser()
        args = parser.parse_args(['process-image'])
        assert args.quality == 85

    def test_process_image_max_size_argument(self):
        parser = build_parser()
        args = parser.parse_args(['process-image', '--max-size', '5.0'])
        assert args.max_size == 5.0

    def test_process_image_input_argument(self):
        parser = build_parser()
        args = parser.parse_args(['process-image', '--input', 'photo.jpg'])
        assert args.input == 'photo.jpg'

    def test_process_image_input_dir_argument(self):
        parser = build_parser()
        args = parser.parse_args(['process-image', '--input-dir', '/path/to/images'])
        assert args.input_dir == '/path/to/images'

    def test_process_image_input_dir_default(self):
        parser = build_parser()
        args = parser.parse_args(['process-image'])
        assert args.input_dir == './input'

    def test_process_image_output_dir_argument(self):
        parser = build_parser()
        args = parser.parse_args(['process-image', '--output-dir', '/path/to/output'])
        assert args.output_dir == '/path/to/output'

    def test_process_image_output_dir_default(self):
        parser = build_parser()
        args = parser.parse_args(['process-image'])
        assert args.output_dir == './output'

    def test_no_command_sets_command_to_none(self):
        parser = build_parser()
        args = parser.parse_args([])
        assert args.command is None

    def test_process_image_sets_func(self):
        parser = build_parser()
        args = parser.parse_args(['process-image'])
        assert args.func == cmd_process_image


# =============================================================================
# main() tests
# =============================================================================

class TestMain:
    """Tests for main CLI entry point."""

    def test_no_command_shows_help_and_exits_zero(self, capsys):
        with patch('sys.argv', ['semiautomatic']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_keyboard_interrupt_exits_130(self):
        with patch('sys.argv', ['semiautomatic', 'process-image']):
            with patch('semiautomatic.cli.cmd_process_image', side_effect=KeyboardInterrupt):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 130

    def test_exception_exits_1(self, capsys):
        with patch('sys.argv', ['semiautomatic', 'process-image']):
            with patch('semiautomatic.cli.cmd_process_image', side_effect=Exception("Test error")):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "Error: Test error" in captured.err

    def test_successful_command_exits_0(self):
        with patch('sys.argv', ['semiautomatic', 'process-image']):
            with patch('semiautomatic.cli.cmd_process_image', return_value=True):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 0

    def test_failed_command_exits_1(self):
        with patch('sys.argv', ['semiautomatic', 'process-image']):
            with patch('semiautomatic.cli.cmd_process_image', return_value=False):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1


# =============================================================================
# cmd_process_image() tests
# =============================================================================

class TestCmdProcessImage:
    """Tests for process-image command handler."""

    def test_delegates_to_run_process_image(self):
        mock_args = MagicMock()
        with patch('semiautomatic.image.process.run_process_image', return_value=True) as mock_run:
            result = cmd_process_image(mock_args)
            mock_run.assert_called_once_with(mock_args)
            assert result is True


# =============================================================================
# Integration tests
# =============================================================================

class TestCLIIntegration:
    """Integration tests for CLI with actual file operations."""

    def test_process_single_image_via_cli(self, small_image_path, temp_dir):
        """Test processing a single image through CLI."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        with patch('sys.argv', [
            'semiautomatic', 'process-image',
            '--input', str(small_image_path),
            '--output-dir', str(output_dir),
            '--size', '50x50'
        ]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        # Verify output was created
        outputs = list(output_dir.glob('*.jpg'))
        assert len(outputs) == 1

    def test_process_image_with_format_conversion(self, small_image_path, temp_dir):
        """Test format conversion through CLI."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        with patch('sys.argv', [
            'semiautomatic', 'process-image',
            '--input', str(small_image_path),
            '--output-dir', str(output_dir),
            '--format', 'png'
        ]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        outputs = list(output_dir.glob('*.png'))
        assert len(outputs) == 1

    def test_process_image_with_compression(self, small_image_path, temp_dir):
        """Test compression mode through CLI."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        with patch('sys.argv', [
            'semiautomatic', 'process-image',
            '--input', str(small_image_path),
            '--output-dir', str(output_dir),
            '--max-size', '0.01'  # 10KB limit
        ]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        outputs = list(output_dir.glob('*'))
        assert len(outputs) == 1
        # Should be compressed to under 10KB
        assert outputs[0].stat().st_size <= 10 * 1024

    def test_process_batch_from_directory(self, image_directory, temp_dir):
        """Test batch processing from directory."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        with patch('sys.argv', [
            'semiautomatic', 'process-image',
            '--input-dir', str(image_directory),
            '--output-dir', str(output_dir),
            '--size', '0.5'
        ]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        # Should have processed multiple images
        outputs = list(output_dir.rglob('*.*'))
        image_outputs = [f for f in outputs if f.suffix.lower() in {'.jpg', '.png'}]
        assert len(image_outputs) >= 2

    def test_missing_input_file_fails(self, temp_dir):
        """Test that missing input file causes failure."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        with patch('sys.argv', [
            'semiautomatic', 'process-image',
            '--input', str(temp_dir / "nonexistent.jpg"),
            '--output-dir', str(output_dir)
        ]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_empty_input_directory_fails(self, temp_dir, capsys):
        """Test that empty input directory fails with appropriate error."""
        input_dir = temp_dir / "empty_input"
        input_dir.mkdir()
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        with patch('sys.argv', [
            'semiautomatic', 'process-image',
            '--input-dir', str(input_dir),
            '--output-dir', str(output_dir),
            '--size', '0.5'
        ]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            # Empty dir is an error - nothing to process
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert 'No image files found' in captured.err

    def test_no_processing_options_fails(self, temp_dir, capsys):
        """Test that omitting all processing options fails with helpful error."""
        input_dir = temp_dir / "input"
        input_dir.mkdir()
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        with patch('sys.argv', [
            'semiautomatic', 'process-image',
            '--input-dir', str(input_dir),
            '--output-dir', str(output_dir)
        ]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert 'Must specify' in captured.err


# =============================================================================
# Help and version output tests
# =============================================================================

class TestHelpOutput:
    """Tests for help output formatting."""

    def test_main_help_contains_commands(self, capsys):
        with patch('sys.argv', ['semiautomatic', '--help']):
            with pytest.raises(SystemExit):
                main()

        captured = capsys.readouterr()
        assert 'process-image' in captured.out
        assert 'commands' in captured.out.lower()

    def test_process_image_help_shows_size_formats(self, capsys):
        with patch('sys.argv', ['semiautomatic', 'process-image', '--help']):
            with pytest.raises(SystemExit):
                main()

        captured = capsys.readouterr()
        # Should show size format examples
        assert '1920x1080' in captured.out
        assert '0.5' in captured.out
        assert 'Scale' in captured.out or 'scale' in captured.out
