# What is this?

This "world" is a python-crime to monkeypatch the Archipelago world registries so that when the
test suite iterates over them to find all the relevant worlds to test, they are instead served
a subset. This allows a user to easily and without core modifications skip tests on unrelated
(but core) worlds.

### Requirements

While there may be a way to use this with python `unittest`, I currently only support `pytest`.
If you haven't already installed `pytest` simply install this world and run `ModuleUpdate.py`
and that core script will pip install the defined requirements like any other world.

### Configuration

The `test_patch.py` file has a hard-coded list of game names that are allowed in the custom
iteration given to the generic test suite, in order to test your own games instead of mine
edit that tuple.

### Usage

In order to actually initialize the monkeypatch make sure to list the `_monkeypatch` folder first
in your target folders when using pytest ex `python -m pytest worlds/_monkeypatch .`. This will
initialize the patch, then run all the discoverable tests in the entire repo. Note that this 
command will include world tests as well, to run just the generic tests (in `test/`) you can use
`python -m pytest worlds/_monkeypatch test` and to run the generic tests and your own world's
test you can use `python -m pytest worlds/_monkeypatch test worlds/my_world`.

### Notes

* If you do not explicitly include the monkeypatch world first (ex. by not specifying
  folders at all), the registry will not be edited before the generic test suite runs, making
  effectively no impact on test runs.
* I have not dug further into webhost test failures, they likely have some cutout that will
  be required for their testing needs that I haven't done yet.
