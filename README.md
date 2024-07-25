# Ubo GUI

GUI sdk for [Ubo Pod](https://github.com/ubopod)

## 📋 Requirements

- [Ubo Pod](https://github.com/ubopod)
- [headless-kivy-pi](https://github.com/ubopod/headless-kivy-pi)

## 📦 Installation

You can install it using this handle: headless-kivy-pi@git+<https://github.com/ubopod/ubo-gui.git>

```sh
# pip:
pip install headless-kivy-pi@git+https://github.com/ubopod/ubo-gui.git
# poetry:
poetry add headless-kivy-pi@git+https://github.com/ubopod/ubo-gui.git
```

## 🛠 Usage

Checkout [Ubo App](https://github.com/ubopod/ubo-app) to see a sample implementation.

## 🤝 Contributing

You need to have [Poetry](https://python-poetry.org/) installed on your machine.

To install poetry in Raspbian you need to follow these instructions to install rust compiler, this is temporary until [this issue](https://github.com/python-poetry/poetry/issues/7645) is resolved:

```sh
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
sudo apt-get install pkg-config libssl-dev
curl -sSL https://install.python-poetry.org | python3 -
```

After having poetry, to install the required dependencies, run the following command:

```sh
poetry install --with dev
```

Also be aware of [this issue](https://github.com/python-poetry/poetry/issues/1917) and until it is resolved you can manually disable keyring by prefixing your poetry commands like this:

```sh
PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring poetry install
```

You can run linter over whole codebase by running this command:

```sh
poetry run poe lint
```

### Subscriptions

The subscriptions are divided into three groups:

- Screen subscriptions are those assigned to a particular stack item, but their handlers doesn't change anything in the `StackItem` itself.
  The handler just changes something on the rendered screen and if that stack item is not visible, the handler doesn't need to be called.
  Therefore these subscriptions are cleared when the current screen is changed.
  Samples:
  - `items` of the currently visible menu
  - `title` of the currently visible screen
- Menu subscriptions are those assigned to a particular menu. Like screen subscriptions, they are cleared when the current screen is changed. They also get cleared when the menu is scrolled.
  Samples:
  - `heading` of a headed menu
  - `sub_heading` of a headed menu
  - `placeholder` of a menu
- Stack item subscriptions are those assigned to a particular stack item. They are cleared when the stack item is popped. They stay alive as long as the stack item is in the stack, even if it is in the background.
  In other words, unlike the other two, they are not cleared when, for example, a sub-menu or an application is opened on top of the current stack item.
  Samples:
  - `menu` of an item

### ⚠️ Important Note

Make sure to run `poetry run poe download_font` to download Material Symbols font.

## 🔒 License

This project is released under the Apache-2.0 License. See the [LICENSE](./LICENSE)
file for more details.
