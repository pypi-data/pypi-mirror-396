# python3-cyberfusion-wordpress-support

Library for WordPress.

# Install

## PyPI

Run the following command to install the package from PyPI:

    pip3 install python3-cyberfusion-wordpress-support

Next, install the following software:

* WP-CLI, according to the [documentation](https://make.wordpress.org/cli/handbook/guides/installing/#recommended-installation) or using [Homebrew](https://formulae.brew.sh/formula/wp-cli). WP-CLI is not required to run tests (automatically downloaded on every suite run).
* MariaDB client (required by WP-CLI), possibly using [Homebrew](https://formulae.brew.sh/formula/mysql-client).

## Debian

Run the following commands to build a Debian package:

    mk-build-deps -i -t 'apt -o Debug::pkgProblemResolver=yes --no-install-recommends -y'
    dpkg-buildpackage -us -uc

# Configure

No configuration is supported.

# Usage

See code.
