# Featureform Python Client

## Overview

Featureform’s Python client is a SDK for defining, managing and serving resources (e.g. infrastructure providers, data sources, transformations, etc.). At a high level, the API is divided into two parts:

* Registration: register data stores (e.g. PostgreSQL), data sources (e.g. tables or CSV files) as resources or get and/or list previously registered resources
* Serving: retrieve training sets and features for offline training or online inference

## Requirements

* Python 3.9-3.12

## Setting Up Your Local Development Environment

### Step 1: Install gRPC and Protocol Buffer Tooling

See grpc.io for instructions on installing the [protocol buffer compiler](https://grpc.io/docs/protoc-installation/) for your OS and language-specific plugins for [Golang](https://grpc.io/docs/languages/go/quickstart/#prerequisites) (**NOTE**: the Golang dependencies can also be installed via [Homebrew](https://brew.sh/).)

### Step 2: Install uv and Sync Dependencies

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if you haven't already. Then sync the project dependencies:

```shell
> uv sync --group dev
```

This creates a virtual environment and installs all required dependencies, including the `featureform` client in editable mode.

### Step 3: Compile API Protocol Buffers and Python Stub

The shell script `gen_grpc.sh` has been provided for convenience. Change the file access permissions to make it executable and run it:

```shell
> chmod +x gen_grpc.sh
> ./gen_grpc.sh
```

### Step 4: Optionally Run Client Test Suite

To ensure your changes haven’t broken the client, run the test suite with the following make target:

```shell
> make pytest
```

## Outcome

With the steps above successfully completed, you should have the `featureform` CLI command accessible via `uv run`:

```shell
> uv run featureform -h
```

To further verify that your setup is complete and correct, you may optionally walk through the [Quickstart](https://docs.featureform.com/quickstart-local) tutorial. You may put the `definitions.py` file at the root of the project, which won’t be ignored by Git, or use a URL to a file (e.g. hosted on GitHub).
