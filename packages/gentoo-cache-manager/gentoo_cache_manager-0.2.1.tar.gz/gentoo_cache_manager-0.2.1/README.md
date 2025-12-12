# 🗃️ Gentoo Cache Manager

[![CI][ci-badge]][ci]
[![Coverage][cov-badge]][cov]
[![License][license-badge]][license]
[![Version][ver-badge]][pypi]
[![Python][py-badge]][pypi]

**Gentoo Cache Manager** aims to help you tweaking build cache settings for individual packages in [Gentoo Linux][gentoo] and some [Gentoo-based][gentoo-based] operating systems.

## 🧑🏽‍🔬 Usage

To enable [ccache][ccache] for `sys-libs/glibc`, run:
```shell
gcm enable glibc
```

To disable it, run:
```shell
gcm disable glibc
```

To explore all available commands, run:
```shell
gcm --help
```

[ci-badge]: https://img.shields.io/github/actions/workflow/status/Jamim/gentoo-cache-manager/ci.yml.svg
[ci]: https://github.com/Jamim/gentoo-cache-manager/actions/workflows/ci.yml
[cov-badge]: https://codecov.io/github/Jamim/gentoo-cache-manager/graph/badge.svg
[cov]: https://app.codecov.io/github/Jamim/gentoo-cache-manager
[license-badge]: https://img.shields.io/github/license/Jamim/gentoo-cache-manager
[ver-badge]: https://img.shields.io/pypi/v/gentoo-cache-manager
[pypi]: https://pypi.org/project/gentoo-cache-manager/
[py-badge]: https://img.shields.io/pypi/pyversions/gentoo-cache-manager
[license]: https://github.com/Jamim/gentoo-cache-manager/blob/main/LICENSE
[gentoo]: https://www.gentoo.org
[gentoo-based]: https://wiki.gentoo.org/wiki/Distributions_based_on_Gentoo
[ccache]: https://wiki.gentoo.org/wiki/Ccache
