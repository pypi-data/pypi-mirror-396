import os
import json
import jwt
from jwt import PyJWKClient
from jwt.exceptions import ExpiredSignatureError
from datetime import datetime
from datetime import timezone
from eas2cli.models import Tokens
from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError


def _tok2dict(tok: str, validate: bool = False) -> dict:
    if validate:
        jwks_client = PyJWKClient("https://geofon.gfz.de/eas2/jwk")
        signing_key = jwks_client.get_signing_key_from_jwt(tok)
        try:
            rawtoken = jwt.decode(tok, signing_key, audience=["fdsn", "eas"], algorithms=['RS256'])
        except ExpiredSignatureError as e:
            raise Exception(str(e))
    else:
        rawtoken = jwt.decode(tok, options={"verify_signature": False})
    for key, value in rawtoken.items():
        if key in ('iat', 'exp') and isinstance(value, (int, float)):
            rawtoken[key] = datetime.fromtimestamp(value).isoformat()
        # print(key, type(value))
    return rawtoken


def readtokens(tokenfile: str = '~/.eidajwt') -> Tokens:
    tokenfile = os.path.expanduser(tokenfile)
    try:
        with open(tokenfile, 'rt') as fin:
            tokens = Tokens(**json.loads(fin.read()))
    except Exception:
        raise Exception('There is a problem reading your available tokens.')
    return tokens


def _silentrefresh(reftok: str, tokenfile: str = '~/.eidajwt', refresh: str = 'https://geofon.gfz.de/eas2/token'):
    postdata = {
        'grant_type': 'refresh_token',
        'refresh_token': reftok
    }
    try:
        with urlopen(refresh, data=urlencode(postdata).encode()) as newtok:
            newtokbytes = newtok.read().decode()
            try:
                newtokens = Tokens(**json.loads(newtokbytes))
            except Exception:
                raise Exception("The tokens received could not be properly read.")
    except HTTPError as e:
        if e.status == 400:
            err = e.read().decode()
            errjson = json.loads(err)
            raise Exception(str(errjson))
        raise Exception("There was an HTTP error while refreshing the tokens.")
    # Check that the new access token is valid
    try:
        atnew = _tok2dict(newtokens.access_token, validate=True)
    except Exception as e:
        raise Exception("There was an error validating the new access token. %s" % (str(e),))
    # Save in the default configuration
    with open(os.path.expanduser(tokenfile), 'wt') as fout:
        fout.write(newtokbytes)


def gettoken() -> str:
    for retry in range(3):
        toks = readtokens()
        accdict = jwt.decode(toks.access_token, options={"verify_signature": False})
        if accdict['exp'] > (datetime.now(tz=timezone.utc).timestamp() + 300):
            return toks.access_token
        _silentrefresh(toks.refresh_token)
