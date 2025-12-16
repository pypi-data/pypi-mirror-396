# RefCheck

RefCheck is a simple tool for finding broken references and links in Markdown files.

```text
usage: refcheck [OPTIONS] [PATH ...]

positional arguments:
  PATH                  Markdown files or directories to check

options:
  -h, --help            show this help message and exit
  -e, --exclude [ ...]  Files or directories to exclude
  -cm, --check-remote   Check remote references (HTTP/HTTPS links)
  -nc, --no-color        Turn off colored output
  -v, --verbose         Enable verbose output
  --allow-absolute      Allow absolute path references like [ref](/path/to/file.md)
```

[![Downloads](https://static.pepy.tech/badge/refcheck)](https://pepy.tech/project/refcheck)
[![CI/CD](https://github.com/flumi3/refcheck/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/flumi3/refcheck/actions/workflows/ci-cd.yml)
[![codecov](https://codecov.io/gh/flumi3/refcheck/graph/badge.svg?token=YOUR_TOKEN)](https://codecov.io/gh/flumi3/refcheck)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Coverage](https://img.shields.io/badge/coverage-80%25-green.svg)

## Features

- 🔍 **Comprehensive Reference Detection** - Find and validate various reference patterns in Markdown files
- ❌ **Broken Link Highlighting** - Quickly identify broken references with clear error messages
- 📁 **File Path Validation** - Support for both absolute and relative file paths to any file type
- 🌐 **Remote URL Checking** - Validate external HTTP/HTTPS links (optional with `--check-remote`)
- 🎯 **Header Reference Validation** - Verify links to specific sections within Markdown files
- 🛠️ **User-Friendly CLI** - Simple and intuitive command-line interface
- ⚙️ **CI/CD Ready** - Perfect for automated quality checks in your documentation workflows
- 🎨 **Colored Output** - Clear, color-coded results for easy scanning (disable with `--no-color`)
- 📊 **Detailed Reporting** - Summary statistics and line-by-line reference validation
- 🚀 **Pre-commit Integration** - Available as a pre-commit hook for automated validation

## Installation

RefCheck is available on PyPI:

```bash
pip install refcheck
```

## Examples

```text
$ refcheck README.md

[+] 1 Markdown files to check.
- README.md

[+] FILE: README.md...
README.md:3: #introduction - OK
README.md:5: #installation - OK
README.md:6: #getting-started - OK

Reference check complete.

============================| Summary |=============================
🎉 No broken references!
====================================================================
```

```text
$ refcheck . --check-remote

[+] Searching for markdown files in C:\Users\flumi3\github\refcheck ...

[+] 2 Markdown files to check.
- tests\sample_markdown.md
- docs\Understanding-Markdown-References.md

[+] FILE: tests\sample_markdown.md...
tests\sample_markdown.md:39: /img/image.png - BROKEN
tests\sample_markdown.md:52: https://www.openai.com/logo.png - BROKEN

[+] FILE: docs\Understanding-Markdown-References.md...
docs\Understanding-Markdown-References.md:42: #local-file-references - OK

Reference check complete.

============================| Summary |=============================
[!] 2 broken references found:
tests\sample_markdown.md:39: /img/image.png
tests\sample_markdown.md:52: https://www.openai.com/logo.png
====================================================================
```

## Pre-commit Hook

RefCheck is also available as pre-commit hook!

```yaml
- repo: https://github.com/flumi3/refcheck
  rev: v0.4.1
  hooks:
    - id: refcheck
      args: ["docs/", "-e", "docs/filetoexclude.md"] # e.g. scan the docs/ folder and exclude a file
```

For more advanced configuration options, see the [Integration Guide](docs/Integration-Guide.md).

## Contributing

Contributions are welcome!

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup instructions
- Commit message conventions
- Code quality standards
- Testing requirements
- Pull request guidelines

## Documentation

For more detailed information, check out the documentation:

- [CLI Reference](docs/CLI-Reference.md) - Complete command-line options and usage
- [Integration Guide](docs/Integration-Guide.md) - CI/CD and workflow integration
- [Examples](docs/Examples.md) - Real-world usage examples

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
