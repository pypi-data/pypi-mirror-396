# Sentinel Logger

[![PyPI version](https://badge.fury.io/py/sentinel-logger.svg)](https://pypi.org/project/sentinel-logger/)
[![Python versions](https://img.shields.io/pypi/pyversions/sentinel-logger.svg)](https://pypi.org/project/sentinel-logger/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Lightweight Python middleware for logging HTTP requests to your Sentinel backend. Zero-config observability for Flask, Django, FastAPI, and any WSGI/ASGI framework.

## Features

- ✨ **Framework agnostic** - Works with Flask, Django, FastAPI, Starlette, Bottle, Pyramid
- 🚀 **Low latency** - Background thread with 500ms flush interval
- 🔄 **Smart retries** - Exponential backoff with jitter (max 5 attempts)
- 🎯 **Reliable** - Keep-alive connections, bounded queue (10k items)
- 🛡️ **Safe** - Drops 4xx errors (no retry for client mistakes)
- 📦 **Tiny** - Single dependency (`requests`)

## Installation

```bash
pip install sentinel-logger