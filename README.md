# Ubo GUI

GUI manager for [Ubo Pod](https://github.com/ubopod)

## ⚡️ Requirements

- [Ubo Pod](https://github.com/ubopod)
- [headless-kivy-pi](https://github.com/sassanh/headless-kivy-pi)

## 📦Installation

You can install it using this handle: headless-kivy-pi@git+<https://github.com/sassanh/ubo-gui.git>

```sh
# pip:
pip install headless-kivy-pi@git+https://github.com/sassanh/ubo-gui.git
# poetry:
poetry add headless-kivy-pi@git+https://github.com/sassanh/ubo-gui.git
```

## 🚀 Usage

Checkout [the menu demo](./demo/menu.py) to see a sample usage. You can run it with this command:

```sh
poetry install --with demo # You also need `--with development` if you want to run it on a non-raspberry machine
poetry run demo-menu
```

## ⚒️ Contribution

You need to have [Poetry](https://python-poetry.org/) installed on your machine.

To install poetry in Raspbian you need to follow these instructions to install rust compiler, this is temporary until [this issue](https://github.com/python-poetry/poetry/issues/7645) is resolved:

```sh
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
sudo apt-get install pkg-config libssl-dev
curl -sSL https://install.python-poetry.org | python3 -
```

After having poetry, to install the required dependencies, run the following command:

```sh
poetry install --with development
```

Also be aware of [this issue](https://github.com/python-poetry/poetry/issues/1917) and until it is resolved you can manually disable keyring by prefixing your poetry commands like this:

```sh
PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring poetry install
```

You can run linter over whole codebase by running this command:

```sh
poetry run poe lint
```

### ⚠️ Important Note

Make sure to run `poetry run poe download_font` to download Material Symbols font.

## 📜 License

This project is released under the Apache-2.0 License.
