<div align = center>

<h1>CYS-403 Project</h1>

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/zefr0x/cys403_project/main.svg)](https://results.pre-commit.ci/latest/github/zefr0x/cys403_project/main)
[![release](https://github.com/zefr0x/cys403_project/actions/workflows/release.yml/badge.svg)](https://github.com/zefr0x/cys403_project/actions/workflows/release.yml)

Simple RSA text encryption and image encryption
[Linux](https://en.wikipedia.org/wiki/Linux)
[GUI](https://en.wikipedia.org/wiki/Graphical_user_interface) application.

---

[<kbd><br><b>Install</b><br><br></kbd>](#installation)
[<kbd><br><b>Contribute</b><br><br></kbd>](CONTRIBUTING.md)

---

<br>

</div>

## Requirements

- [GTK4](https://www.gtk.org/)
- [Adwaita](https://gitlab.gnome.org/GNOME/libadwaita/)

## Installation

### Git

> You need to have [`meson`](https://mesonbuild.com/) and
> [`xgettext`](https://www.gnu.org/software/gettext/) installed in your system.
>
> You need python modules listed in
> [`requirements/requirements.in`](requirements/requirements.in) installed in
> your python environment.

```shell
git clone https://github.com/zefr0x/cys403_project.git
cd cys403_project
meson setup builddir
meson install -C builddir
```

## Acknowledgments

- **[Bottles](https://github.com/bottlesdevs/Bottles)** - For showing how to
  deal with a python project using [Meson](https://mesonbuild.com/).
- **[Dialect](https://github.com/dialect-app/dialect)** - For showing how to
  deal with CLI in python PyGObject application.
