# Changelog

## Version 0.6.0

- refactor: optimize `MenuWidget` and improve its api to use kivy properties
- refacotr: make `MenuWidget` use transitions for all its screen switches

## Version 0.5.0

- chore: drop support for python 3.9 and 3.10
- refactor: improve typings

## Version 0.4.5

- fix: crash when empty header menu page is rendered

## Version 0.4.4

- chore: migrate from poetry groups to poetry extras

## Version 0.4.1

- chore: fix quotes

## Version 0.4.0

- chore: update dependencies to their latest versions
- chore: extract demo from repository and bundle it as to be ubo-app
- chore: rename python module from ubo to ubo_gui
- docs: update README with new repository locations

## Version 0.3.7

- style: improve styling of notifications and menus
- refactor: replace hardcoded short ItemWidget width with a constant

## Version 0.3.6

- refactor: propagate buttons to current_application
- fix: NotificationWidget scrolling and improve its layout

## Version 0.3.5

- refactor: use Factory.register to register widgets

## Version 0.3.4

- fix: provide AnimatedSlider for menu.kv

## Version 0.3.3

- feat: add ellipses for labels where applicable

## Version 0.3.2

- chore: add CHANGELOG.md

## Version 0.3.1

- feat: add AnimatedSlider and use it as the menu's scrollbar

## Version 0.3.0

- feat: add ubo keypad
- feat: add scrollbar to menus

## Version 0.2.5

- fix: add font assets to the package

## Version 0.2.3

- refactor: update code structure so that all packages are sub-packages of a single package named ubo

## Version 0.2.2

- fix: use dp for the radius of rounded rectangles
- feat: implement notifications and add sample usage to menu demo app
- feat: implement WifiPrompt in demo/menu.py as an example of PromptWidget usage and as an example of application launcher menu item
- refactor: change Widgets with nested BoxLayouts to simple BoxLayouts
- feat: implement application launcher menu items
- feat: add prompt widget
- fix: gauge sizing should use dp() to avoid inconsistency in different platforms
- docs: add instructions for running demo to README.md
- feat: add clock widget and back icon to the footer
- feat: add VolumeWidget and GaugeWidget and use them in home page
- refactor: better organize menu widget in multiple files
- fix: change header.text only when the default header label is in use
- chore: add poethepoet to dependencies
- docs: add basic information in README.md
- feat: replace old icon_path, etc with new icon field for menu items, it uses material symbols icon font to render icons
- fix: don't render non-existing item widgets in a menu page
- docs: update menu demo to use latest features
- chore: add lint script entry to pyproject.toml
- feat: allow setting is_short property of menu items from Item TypedDict class
- feat: add HeadlessMenu for rendering menus without a heading in the first page, it completes HeadedMenu which is the old Menu class
- feat: support function values for items field of a menu
- style: change default color of menu items to ubo blue
- feat: add is_short property to items
- refactor: extract page widget from menu widget
- chore: improve dependencies for raspberry pi
- fix: install headless-kivy-pi from its github repository instead of a local path
- feat: add icons to menu item and improve their style

## Version 0.2.1

- refactor: rewrite the demo application using app class

## Version 0.2.0

- feat: add app class providing a general layout for ubo gui applications
- refactor: decouple demo application from the core functionality and use its provided api instead

## Version 0.1.0

- chore: move headless-kivy-pi's pagination demo to a new repository
