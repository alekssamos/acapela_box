from unittest.mock import patch

from click.testing import CliRunner

from acapela_box.__main__ import main
from acapela_box.base import AcapelaBoxError


def test_main():
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code == 2  # Not enough arguments

    result = runner.invoke(main, ['foo', 'bar', 'baz', '--username', 'foo'])
    assert result.exit_code == -1

    result = runner.invoke(main, ['foo', 'bar', 'baz', '--password', 'bar'])
    assert result.exit_code == -1

    with patch('acapela_box.base.AcapelaBox.get_mp3_url') \
            as get_mp3_url_method:
        get_mp3_url_method.return_value = 'http://foo.com/path/to/file.mp3'
        result = runner.invoke(main, ['French (France)', 'bar', 'baz'])
        assert result.output == 'http://foo.com/path/to/file.mp3\n'

        with patch('acapela_box.base.AcapelaBox.authenticate') \
                as authenticate_method:
            authenticate_method.side_effect = AcapelaBoxError

            result = runner.invoke(main, ['French (France)', 'bar', 'baz',
                                          '--username', 'foo',
                                          '--password', 'bar'])
            assert result.exit_code == -2

            authenticate_method.side_effect = None
            result = runner.invoke(main, ['French (France)', 'bar', 'baz',
                                          '--username', 'foo',
                                          '--password', 'bar'])
            assert result.output == 'http://foo.com/path/to/file.mp3\n'
