# Changelog

## Version 0.13.8

- refactor: set key of menu items returned by the action of `ActionItem` if the `ActionItem` itself has a key

## Version 0.13.7

- refactor: handle `text` field of `SpinnerWidget` when it contains kivy markup but yet reduces to `` when markup is removed

## Version 0.13.6

- fix: add `SpinnerWidget` to kivy factory

## Version 0.13.5

- refactor: use `SpinnerWidget` in place of `Label` for all dynamic contents labels, setting its `text` to `` will spin it, otherwise it behaves like a `Label`

## Version 0.13.4

- chore: migrate from poetry to uv for the sake of improving performance and dealing with conflicting sub-dependencies
- feat: add spinner widget which doesn't trigger whole screen renders and uses new local renders of headless-kivy
- chore: update to the latest version of headless-kivy

## Version 0.13.3

- fix: make `PromptWidget` inherit `PageWidget`

## Version 0.13.2

- refactor: avoid loading kivy when constants are imported

## Version 0.13.1

- feat: widen the notification text horizontally if it doesn't have any actions on the left

## Version 0.13.0

- fix: updating items of the pages after the first page not being visible
- refactor: merge `HeaderMenuPageWidget` and `NormalMenuPageWidget` into `MenuPageWidget`
- refactor: keep a clone of menu-page widget as Kivy needs the source and target widgets to be different for transitions while going up and down in a menu needs a transition of the same widget to itself as we just change its items and don't recreate it

## Version 0.12.5

- fix: `go_home` should clear the selection of root before setting `stack`

## Version 0.12.4

- fix: going home from home caused a bad state

## Version 0.12.3

- feat: keep track of the selections, so that we can replace all the deep selections of an item when it's replaced

## Version 0.12.2

- fix: headed menu item presentation logic

## Version 0.12.1

- fix: headed menu item selection logic
- refactor: make the background band width of the `ProgressRingWidget` configurable via `background_band_width` property

## Version 0.12.0

- refactor: just change the items of the menu when items are changed, instead of creating a whole new menu widget
- feat: add progress to `ItemWidget`, reflect it in its look and optimize its rendering for rapid re-renders
- feat: add `ProgressRingWidget` widget

## Version 0.11.17

- feat: add `_visual_snapshot` to visualize the state of stack for debugging purposes
- fix: avoid user selecting a second item while the screen is being transitioned
- fix: improving the logic of replacing an item in the deep layers of stack
- fix: no more blinking when the content is not changed

## Version 0.11.16

- build: update `headless-kivy` to the latest version

## Version 0.11.15

- fix: set duration of `0` for when `_no_transition` is passed to `_switch_to` method

## Version 0.11.14

- fix: pass duration with value of `0` to `Screen`'s transition runner to avoid flickering of the screen

## Version 0.11.13

- build: update headless-kivy-pi to the latest version

## Version 0.11.12

- build: update headless-kivy-pi to the latest version

## Version 0.11.11

- fix(MenuWidget): the menu doesn't override the top-most item whenever an arbitrary sub-menu's subscription reports a change, instead, it updates the item in the stack for which the change was reported
- refactor(PromptWidget): `PromptWidget` now exposes an `items` list property to be compatible with other subclasses of `PageWidget` so that tests can interact with it easier

## Version 0.11.10

- fix(MenuWidget): render placeholder when the menu is empty and `render_surroundings` is `True`

## Version 0.11.9

- feat(MenuWidget): add methods for directly selecting an `Item`

## Version 0.11.8

- fix(MenuWidget): align items with the physical buttons

## Version 0.11.7

- feat(MenuWidget): add `go_home` method, resetting the stack to a single element root menu

## Version 0.11.6

- refactor(MenuWidget): dispatch `on_close` event on the `PageWidget` instance when it is closed, to close a `PageWidget` instance, one should call `close_application`

## Version 0.11.5

- fix(MenuWidget): avoid opening an `ActionItem`'s `action` return value twice if it is a `PageWidget` class
- refactor(MenuWidget): improve opening/closing application logic to avoid race conditions
- refactor(PageWidget): add `__repr__` to help debugging and logging `PageWidget`s
- refactor(MenuWidget): use `mainthread` decorator in transitions only when necessary
- refactor(ItemWidget): increase the length of non-short items (decrease the right margin from 30 to 6)

## Version 0.11.4

- refactor(NotificationWidget): remove all the logic and make it solely a view

## Version 0.11.3

- feat(Menu): action items can now return not only the application class, but also instances of applications too
- fix(QRCodeWidget): set default value of `fit_mode` to `contain`

## Version 0.11.2

- refactor(NotificationWidget): improve layout of the notification widget

## Version 0.11.1

- fix(menu): use application's title as the title of the menu if it's provided
- fix(menu): add the title space to the application if it has no title

## Version 0.11.0

- feat(Menu): render faded next and previous menu items to induce there are more items in the menu and it can be scrolled
- refactor(core): add colors to list of global constants to avoid hardcoding
- refactor(AnimatedSlider): not using the default look, replaced with the one designed in figma
- refactor(ItemWidget): add `opacity` field
- ci(github): add changelog to the release notes

## Version 0.10.8

- fix(regression): handle return value of the action in `ActionItem` when it's callable
- refactor(notification): make the icon smaller and make sure it is rendered on top

## Version 0.10.7

- fix(menu): not assume the return value of the action in `ActionItem` is a `Menu` if it is not an `application`

## Version 0.10.6

- feat: info action for the `NotificationWidget`

## Version 0.10.5

- refactor: enable `markup` for labels

## Version 0.10.4

- fix(menu): avoid closing all applications when a single application is closed

## Version 0.10.3

- feat(menu): add placeholder for the menu when it's empty

## Version 0.10.2

- fix(regression): keep the menu responsive even with rapid switches of the screen-manager

## Version 0.10.1

- fix: update remaining material symbols icons

## Version 0.10.0

- refactor: drop material symbols font and use `ArimoNerdFont` instead to bring all the icons of fa, md, mdi, etc

## Version 0.9.9

- chore: update to the latest version of headless-kivy-pi 0.7.1

## Version 0.9.8

- chore: update to the latest version of headless-kivy-pi

## Version 0.9.7

- feat: add `QRCodeWidget`

## Version 0.9.6

- refactor: use headless-kivy-pi 0.6.0
- refactor: make `on_title` callback use weakref to avoid memory leaks

## Version 0.9.5

- chore: use git-lfs to track material font

## Version 0.9.4

- chore: GitHub workflow to publish pushes on `main` branch to PyPI
- chore: create GitHub release for main branch in GitHub workflows
- chore: create Pyright stub files for Kivy
- refactor: fix lint issues and typing issues

## Version 0.9.3

- fix: close_application now actually closes the passed application

## Version 0.9.2

- fix: queue transitions instead of letting the last transition interrupt the active one

## Version 0.9.1

- hotfix: remove debug background rectangle

## Version 0.9.0

- refactor: remove `current_application` and `current_menu` from `MenuWidget`, just keep them as a proxy for the top item of the `stack`
- refactor: clean subscriptions in different levels of screen, widget and item
- feat: allow action items to return subscribable menus
- feat: add `logger` and log subscriptions

## Version 0.8.0

- feat: add a mechanism to sync properties with subscribable values (defined in python-redux). applied for these properties: - `MenuWidget`: 1. `application` 1. `sub_menu` 1. `heading` of headed menu 1. `sub_heading` of headed menu 1. `items` of menu 1. `title` of menu - `ItemWidget`: 1. `label` 1. `is_short` 1. `color` 1. `background_color` 1. `icon`

## Version 0.7.9

- fix: don't call `application` if it's a subclass of `PageWidget`

## Version 0.7.8

- feat: make all fields of `Menu` and `Item` and their sub classes accept callables

## Version 0.7.7

- fix: dispatch `on_close` when a `PageWidget` is left (`on_leave` is dispatched)
- style: improve layout of `HeadedMenu`

## Version 0.7.6

- fix: let `title` in `PageWidget` accept `None`

## Version 0.7.5

- fix: allow `None` value for `title` property of `PageWidget`

## Version 0.7.4

- fix: avoid unnecessary property caching causing temporary inaccurate state for `MenuWidget`

## Version 0.7.2

- feat: different transitions for different actions of `MenuWidget`
- refactor: add default values for properties of `ItemWidget`
- style: improve layout of `NotificationWidget`

## Version 0.7.1

- feat: add `on_dismiss` event to `NotificationWidget`
- refactor: extract `DANGER_COLOR` and `SUCCESS_COLOR` previously hardcoded in `PromptWidget`

## Version 0.7.0

- refactor: migrate from `TypedDict` to `Immutable` of python-immutable for the sake of better compatibility with python-redux
- refactor: remove `NotificationManager` as it is beyond the scope of this package
- refactor: minor improvements in typehints

## Version 0.6.5

- docs: update `README.me`

## Version 0.6.4

- feat: make `MenuWidget` subscribe to the items of the current menu if it provides a `subscribe` property

## Version 0.6.3

- refactor: make prompt widget responsive to changes of its items

## Version 0.6.2

- refactor: make constants globally accessible for all kv files with `UBO_GUI_` prefix

## Version 0.6.1

- fix: checking availability of `PromptWidget` items would cause a crash

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
