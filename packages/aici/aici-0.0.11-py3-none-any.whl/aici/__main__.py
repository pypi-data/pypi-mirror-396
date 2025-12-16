"""
aici  CLI for AI

this module is designed in the form of a CLI to make it easier to invoke AI API calls from other tools.

This file handles the execution when called with python -m aici.

`python -m aici <arg1> <arg2>`

"""
import aici
from .main import main
from argparse import ArgumentParser

main()


