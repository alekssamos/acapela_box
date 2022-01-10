"""Entry point."""

import click

from .base import AcapelaBox, AcapelaBoxError


@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.argument("language")
@click.argument("voice")
@click.argument("text")
@click.option("--username", help="Acapela Box username (if authenticating).")
@click.option("--password", help="Acapela Box password (if authenticating).")
@click.option("--spd", default=180, help="Speech rate (speed).")
@click.option("--vct", default=100, help="Speech velocity (pitch).")
@click.option("--format", default=100, help="""
Audio format. A number from 1 to 5. It can be:
    1. MP3;
    2. WAV 22kHz;
    3. WAV a-law;
    4. WAV \u00b5-law;
    5. WAV 8kHz;
""")
@click.option("--byline", default=0, help="Export by line?")
def main(language, voice, text, username=None, password=None, spd=None, vct=None, format=None, byline=None):
    """Fetch generated tts sounds from Acapela Box."""
    acapela_box = AcapelaBox()

    # The two options must be provided together.
    if username is not None and password is None or \
            password is not None and username is None:
        click.secho("Please provide *BOTH* username and password, or nothing "
                    "at all.", fg="red")
        raise SystemExit(-1)
    else:
        do_authenticate = username is not None and password is not None

    try:
        if do_authenticate:
            acapela_box.authenticate(username, password)

        click.echo(acapela_box.get_mp3_url(
            language=language,
            voice=voice,
            text=text,
            spd=spd,
            vct=vct,
            format=format,
            byline=byline
        ))
    except AcapelaBoxError as exn:
        click.secho(str(exn), fg='red')
        raise SystemExit(-2)


if __name__ == '__main__':
    main()
