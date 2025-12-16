# https-login-server

[![PyPI version](https://badge.fury.io/py/https-login.svg)](https://badge.fury.io/py/https-login)


A tiny HTTPS file server (similar to `python -m http.server`) with:
- temporary self-signed TLS certificate (generated at runtime)
- simple login page
- PBKDF2 password hashing + passfile

## Install
```bash
pip install https-login
```

## Usage
```bash
https-login --set-password "mypassword"
https-login --dir . --port 8443 --host localhost
````
or
```bash
python -m https_login.server
```

## Notes

Self-signed cert => browser warning is expected.