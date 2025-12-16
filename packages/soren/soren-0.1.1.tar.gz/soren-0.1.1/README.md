# Soren CLI

Command-line interface for the Soren AI evaluation framework.

## Installation

```bash
pip install soren
```

## Usage

### Login

Authenticate with your Soren account:

```bash
soren login
```

You can also provide credentials directly:

```bash
soren login --email your@email.com --password yourpassword
```

### Run Evaluations

Create and run an evaluation:

```bash
soren run myproject --dataset mydataset --judge gpt-4
```

### Logout

Clear stored credentials:

```bash
soren logout
```

## Configuration

The CLI stores configuration in `~/.soren/config.json`, including:
- API key (for authentication)
- API URL (defaults to production)

## Environment Variables

- `SOREN_API_KEY`: Set your API key (alternative to `soren login`)
- `SOREN_API_URL`: Override the default API URL

## Development

To install from source:

```bash
pip install -e .
```

## License

MIT
