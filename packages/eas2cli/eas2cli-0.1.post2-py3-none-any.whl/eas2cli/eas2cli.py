from datetime import datetime
from datetime import timezone
import pprint
from urllib.error import HTTPError
import click
import os
import json
import webbrowser
import jwt
from typing import Literal
from pydantic.v1 import ValidationError
from eas2cli.models import Tokens
from eas2cli.core import readtokens
from eas2cli.core import _tok2dict
from eas2cli.core import _silentrefresh
from time import sleep
from urllib.request import urlopen
from urllib.parse import urlencode


__version__ = '0.1post2'


@click.group()
@click.version_option(__version__)
def eas2cli():
    pass


@eas2cli.command()
@click.option('--tokenfile', default='~/.eidajwt',
              help='File where the tokens are stored. Usually "~/.eidajwt".')
def logout(tokenfile: str = '~/.eidajwt'):
    """Remove the file with tokens

    The user will need to manually log in again to be able to get an access token"""
    if click.confirm('If you do this you will need to manually login again to get an access token.\nDo you really want to logout?'):
        try:
            os.remove(os.path.expanduser(tokenfile))
            click.echo('You have been successfully logged out')
        except FileNotFoundError:
            click.echo(message=click.style('Error: ', fg='red'), err=True, nl=False)
            click.echo(message='No tokens have been found.', err=True)
        except Exception as e:
            click.echo(message=click.style('Error: ', fg='red'), err=True, nl=False)
            click.echo(message=str(e), err=True)
    return


@eas2cli.command()
@click.option('--tokenfile', default='~/.eidajwt',
              help='File where the tokens are stored. Usually "~/.eidajwt".')
def login(tokenfile: str = '~/.eidajwt'):
    """Open a webpage to allow the user to login

    After successful login the user can enter the code returned to get the tokens"""
    url = 'https://geofon.gfz.de/eas2/device/code'
    urltoken = 'https://geofon.gfz.de/eas2/token'
    postdata = {'client_id': 'eas2cli'}
    with urlopen(url, data=urlencode(postdata).encode()) as newdev:
        data = json.loads(newdev.read())
    click.echo('Enter user code "%s" at %s' % (data['user_code'], data['verification_uri']))
    webbrowser.open(data['verification_uri'])

    # Prepare request
    postdata = {'client_id': 'eas2cli',
                'device_code': data['device_code'],
                'grant_type': 'urn:ietf:params:oauth:grant-type:device_code'}

    # Sleep for some seconds
    sleep(data['interval'])
    iterations = range(data['interval'], data['expires_in'], data['interval'])
    with click.progressbar(iterations, label='Time remaining to get a token') as bar:
        for it in bar:
            # Sleep for some seconds
            sleep(data['interval'])
            # Try to get the token
            try:
                with urlopen(urltoken, data=urlencode(postdata).encode()) as fin:
                    rawtoken = fin.read().decode()
                    # Verify data
                    datatoken = json.loads(rawtoken)
                    Tokens(**datatoken)
                with open(os.path.expanduser(tokenfile), 'wt') as fout:
                    fout.write(rawtoken)
                break
            except Exception:
                pass
        else:
            click.echo(click.style('No token could be retrieved! Please, try again.', fg='red'))
            return
    click.echo('Token saved in default location!')
    return


@eas2cli.command()
@click.option('--endpoint', default='https://geofon.gfz.de/eas2/token',
              help='URL where a new token can obtained.')
@click.option('--tokenfile', default='~/.eidajwt',
              help='File where the tokens are stored. Usually "~/.eidajwt".')
def refresh(tokenfile: str = '~/.eidajwt', endpoint: str = 'https://geofon.gfz.de/eas2/token'):
    """Refresh the access and id tokens stored locally"""
    try:
        tokens = readtokens(tokenfile)
    except Exception as e:
        click.echo(message=click.style('Error: ', fg='red'), err=True, nl=False)
        click.echo(message=str(e) + ' Try to log in again.', err=True)
        return

    postdata = {
        'grant_type': 'refresh_token',
        'refresh_token': tokens.refresh_token
    }
    try:
        with urlopen(endpoint, data=urlencode(postdata).encode()) as newtok:
            newtokbytes = newtok.read().decode()
            try:
                newtokens = Tokens(**json.loads(newtokbytes))
            except ValidationError:
                click.echo(message=click.style('Error: ', fg='red'), err=True, nl=False)
                click.echo("The tokens received could not be properly read. Wrong format?\n%s" % newtokbytes, err=True)
                return
    except HTTPError as e:
        if e.status == 400:
            err = e.read().decode()
            errjson = json.loads(err)
            # print(errjson)
            click.echo(message=click.style('Error: ', fg='red'), err=True, nl=False)
            click.echo(pprint.pformat(errjson), err=True)
            return

    at = _tok2dict(tokens.access_token)
    # Check that the new access token is valid
    try:
        atnew = _tok2dict(newtokens.access_token, validate=True)
    except Exception as e:
        click.echo(message=click.style('Error: ', fg='red'), err=True, nl=False)
        click.echo("There was an error validating the new access token. %s" % (str(e),))
        return

    # Check that the new ID token is valid and better than the one we already have
    try:
        idnew = _tok2dict(newtokens.id_token, validate=True)
    except Exception as e:
        click.echo(message=click.style('Error: ', fg='red'), err=True, nl=False)
        click.echo("There was an error validating the new ID token. %s" % (str(e),))
        return

    with open(os.path.expanduser(tokenfile), 'wt') as fout:
        fout.write(newtokbytes)


@eas2cli.command()
@click.option('--tokenfile', default='~/.eidajwt',
              help='File where the tokens are stored. Usually "~/.eidajwt".')
@click.option('--validate/--no-validate', default=False,
              help='Declare if tokens must be validated when showing them')
@click.option('--decode/--no-decode', default=True,
              help='Decode token before displaying. Only with "access" and "id" tokens.')
@click.option('--refresh/--no-refresh', default=True,
              help='Refresh the access token if it is not valid or is closed to expire.')
@click.argument('token', default='all', )
def show(token: Literal['access', 'refresh', 'id', 'all'], tokenfile: str = '~/.eidajwt', validate: bool = False,
         decode: bool = True, refresh: bool =True):
    """Show the tokens stored locally and optionally refresh the access token if needed"""
    for retry in range(3):
        try:
            nt = readtokens(tokenfile)
        except Exception as e:
            click.echo(message=click.style('Error: ', fg='red'), err=True, nl=False)
            click.echo(message=str(e) + ' Try to log in again.', err=True)
            return

        rawtoken = jwt.decode(nt.access_token, options={"verify_signature": False})
        if refresh and (rawtoken['exp'] < (datetime.now(tz=timezone.utc).timestamp() + 300)):
            _silentrefresh(nt.refresh_token)
        else:
            break

    if token == 'all':
        for att, value in nt:
            if att == 'refresh_token' or not att.endswith('_token'):
                click.echo('%s: %s' % (click.style(att.removesuffix('_token'), fg='green'), value))
            else:
                try:
                    click.echo('%s: %s' % (click.style(att.removesuffix('_token'), fg='green'),
                                           _tok2dict(value, validate=validate)))
                except Exception as e:
                    click.echo('%s: %s' % (click.style(att.removesuffix('_token') + ' (%s)' % str(e), fg='red'),
                                           _tok2dict(value, validate=False)))

    elif token == 'refresh':
        click.echo('%s: %s' % (click.style('refresh', fg='green'), nt.refresh_token))
    elif token == 'access' and not decode:
        click.echo(nt.access_token)
        return
    elif token == 'id' and not decode:
        click.echo(nt.id_token)
        return
    else:
        try:
            click.echo('%s: %s' % (click.style(token, fg='green'),
                                   _tok2dict(getattr(nt, token + '_token'), validate=validate)))
        except Exception as e:
            click.echo('%s: %s' % (click.style(token, fg='red') + ' (%s)' % str(e),
                                   _tok2dict(getattr(nt, token + '_token'), validate=False)))


if __name__ == '__main__':
    eas2cli()
