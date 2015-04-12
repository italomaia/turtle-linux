#!/usr/bin/env python
"""Point of execution for play.

Configures module path to contain 'lib' and then calls main.main.

"""

import sys
import os


def run(debug=False):
    """Run the game.

    Loads the game library and executes the entry method. Optionally we set
    the debug flag in the constants module before importing anything else
    from the game library.

    """
    try:
        import constants
        constants.DEBUG = debug
    except ImportError, exc:
        print "%s: error: could not find source directory" % SCRIPT_NAME
        sys.exit(1)

    try:
        import main
        main.main()
    except Exception, exc:
        import traceback
        open("error.log", "w").write(traceback.format_exc())
        raise


if __name__ == "__main__":
    # Scipt name and directory
    SCRIPT_NAME = os.path.basename(os.path.join(".", sys.argv[0]))
    SCRIPT_DIR = os.path.dirname(os.path.join(".", sys.argv[0]))

    # Change to the game directory
    os.chdir(SCRIPT_DIR)
    sys.path.insert(0, "lib")

    # Start the actual game
    run()
