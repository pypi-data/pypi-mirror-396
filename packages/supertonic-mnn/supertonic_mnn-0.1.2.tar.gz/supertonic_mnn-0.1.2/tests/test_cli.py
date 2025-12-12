import sys
import os
import pytest
from unittest.mock import MagicMock, patch
import numpy as np

# Add src to path to import supertonic_mnn
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

#sys.modules['MNN'] = MagicMock()
#sys.modules['onnxruntime'] = MagicMock()
#sys.modules['soundfile'] = MagicMock()

from supertonic_mnn.cli import main

@pytest.fixture
def mock_dependencies():
    with patch('supertonic_mnn.cli.ensure_models') as mock_ensure, \
         patch('supertonic_mnn.cli.load_text_to_speech') as mock_load_tts, \
         patch('supertonic_mnn.cli.load_voice_style') as mock_load_style, \
         patch('supertonic_mnn.cli.get_voice_style_path') as mock_get_style_path, \
         patch('soundfile.write') as mock_sf_write:

        # Mock TTS engine
        mock_tts_engine = MagicMock()
        mock_tts_engine.sample_rate = 24000
        # return (wav, duration, rtf)
        # wav is expected to be a list/array where wav[0] is data
        mock_tts_engine.return_value = ([np.zeros(1000)], 1.0, 0.1)
        mock_load_tts.return_value = mock_tts_engine

        # Mock style
        mock_load_style.return_value = {"some": "style"}

        yield {
            'ensure': mock_ensure,
            'load_tts': mock_load_tts,
            'load_style': mock_load_style,
            'get_style_path': mock_get_style_path,
            'sf_write': mock_sf_write,
            'tts_engine': mock_tts_engine
        }

def test_cli_no_args(capsys):
    # Test that running without args prints help or error and returns/exits
    # In the current implementation, main() without args reads from stdin.
    # We should mock stdin or provide args.
    pass

def test_cli_input_text_stdin(mock_dependencies):
    # Mock stdin
    with patch('sys.stdin.read', return_value='Hello world'), \
         patch('sys.argv', ['supertonic-mnn']):
        main()

    mock_dependencies['ensure'].assert_called_once()
    mock_dependencies['load_tts'].assert_called_once()
    mock_dependencies['tts_engine'].assert_called_with('Hello world', {'some': 'style'}, 5, 1.0)
    mock_dependencies['sf_write'].assert_called_once()

def test_cli_input_file(mock_dependencies, tmp_path):
    input_file = tmp_path / "input.txt"
    input_file.write_text("Line 1\nLine 2")
    output_file = tmp_path / "output.wav"

    with patch('sys.argv', ['supertonic-mnn', '-i', str(input_file), '-o', str(output_file)]):
        main()

    assert mock_dependencies['ensure'].call_count == 1
    assert mock_dependencies['load_tts'].call_count == 1
    # Should call tts twice because file has 2 lines
    assert mock_dependencies['tts_engine'].call_count == 2
    # Should write to file twice (separate files)
    # The CLI logic: if >1 lines, it appends index to filename
    # output.wav -> output_1.wav, output_2.wav
    assert mock_dependencies['sf_write'].call_count == 2

def test_cli_custom_args(mock_dependencies):
    with patch('sys.stdin.read', return_value='Test'), \
         patch('sys.argv', ['supertonic-mnn', '--voice', 'Z1', '--speed', '1.2', '--steps', '10']):
        main()

    from unittest.mock import ANY
    mock_dependencies['get_style_path'].assert_called_with('Z1', ANY)
    # Note: DEFAULT_CACHE_DIR is used if not provided, we didn't mock it so checking call args might be tricky if we don't know the exact value.
    # But we can check speed and steps passed to tts_engine
    mock_dependencies['tts_engine'].assert_called_with('Test', {'some': 'style'}, 10, 1.2)

