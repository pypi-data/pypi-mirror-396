# Shopping List

This is a Shopping List app for [Alliance Auth](https://gitlab.com/allianceauth/allianceauth) (AA) 

## Features

- Paste in your Eve/FleetUp fit (with optional multiplier) and then paste in your eve list of assets.  It will run a comparison and let you know what still needs to be purchased.  Now includes equivalence checks

## Installation

Once you have cloned the repo or copied all files into place.

Make sure you are in your venv. Then install it with pip from PyPi or pip in editable mode if downloaded from source:

```bash
pip install cmShoppingList 
or
pip install -e {path_to}/cmShoppingList

```

First add your app to the Django project by adding 'cmShoppingList' to INSTALLED_APPS in `settings/local.py`.

Next perform migrations to add models to the database:

```bash
python manage.py migrate
```

Next initalize all the market types and equivalences

```bash
python manage.py populate_types
```

Next copy all the static data to the output folder

```bash
python manage.py collectstatic --noinput
```

Finally restart your AA setup.

## Permissions

There is only one permission for this application and it's to allow access and show it in the menu

View Shopping List menu item
    *cmShoppingList.basic_access*











