

# Wikibase Redirect Cleanup

Extremely basic **GUI tool** that uses [WikibaseIntegrator](https://github.com/LeMyst/WikibaseIntegrator) to **fix (double) redirects in a wikibase instance**.

<div align="center"><img width="653" height="409" alt="Screenshot 2026-06-04 192624" src="https://github.com/user-attachments/assets/c4135a7a-947a-430f-b73e-7254f36f9f5b"></div>

The functionality is also available by directly running the desired python scripts.

## Purpose

The tool can do 2 *slightly* diferrent things to help clean up your wikibase instance:
- **Fix statement redirects**: for each statement that points to a redirect, this changes the statement to point directly to the target value of the redirect.
- **Resolve double redirects**: for each redirect that points to a redirect, change the initial redirect to point directly at the target value of the second redirect. Running this as much times as necessary will eventually result in a wikibase instance that only has single redirects, which wikibase is able to handle more cleanly than redirect chains.

  To illustrate:
`A -> B, B -> C, C -> D` eventually becomes `A -> D, B -> D, C -> D` after 2 runs.

This tool will not remove the actual redirects themselves (as this information might still be valuable for external references to ids)!

## Usage
### GUI
To use, do the following:
- [**download**](https://github.com/Kunstenpunt/wikibase-redirect-cleanup/releases/latest) the tool
- **launch** the tool (see the [following section](#running-from-source) if you are running from source)
- make sure your **wikibase instance settings** are entered correctly using the corresponding "Wikibase Instance Config" button (these settings are saved in a `json.config` file next to the executable and will be loaded on subsequent launches)

<div align="center"><img width="759" height="291" alt="Screenshot 2026-06-04 192719" src="https://github.com/user-attachments/assets/4fa2ecdf-d245-4a90-884f-cb59c43bff13"></div>

- add your **username** and the **botpassword**
  - username = user that owns the bot (e.g. `WALL-E`)
  - botpassword = BOTNAME@BOTPASSWORD (e.g. `REDIRECTFIXER@123456789`)
- **"Fix statement redirects"** and **"Resolve double redirects"** will start a run of that specific cleanup task. You can cancel a run using the **"Cancel"** button.

The tool can also save wikibase edit error logs to `.csv` files if desired (ideally these files will be empty).

Make sure to create a **bot/botpassword with the correct permissions** (basic rights, high-volume (bot) access, editing existing pages). The user itself should also have the **bot** role.

### Script
Run the `fix_statement_redirects.py` and / or `resolve_double_redirects.py` scripts directly, using username and botpassword as arguments. The wikibase config info should be present in `config.json` next to the script (the default version of this config file will be generated after attempting to run the script once). See the [next section](#running-from-source) for more info.

## Running from source
The tool uses `pipenv` for the environment handling. Install it on your system, preferably together with `pyenv` to handle automatic installation of different python versions. Then run the following to set up the environment:

`pipenv install` and `pipenv install --dev` for the development dependencies (`mypy` and `pyinstaller`)

To run the app:

`pipenv run python src/gui.py`

To run a specific script (fill in `config.json` correctly next to the script for wikibase instance settings):

`pipenv run python src/fix_statement_redirects.py USERNAME BOTNAME@BOTPASSWORD`

`pipenv run python src/resolve_double_redirects.py USERNAME BOTNAME@BOTPASSWORD`

To do the static type check:

`pipenv run mypy`

To generate an executable:

`pipenv run pyinstaller --onefile --windowed --name "Wikibase Redirect Cleanup" src/gui.py`
