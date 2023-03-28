#  DISCO

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 📖 About

DISCO is a cloud-based music catalog management, discovery, and promotion SaaS platform used by professionals to interact within and between the music and media industries.

Basically, every piece of recorded music, that you’ve ever heard has been through a long series of processes (from creation to distribution to promotion) prior to reaching your ears.

## 🛠️ Setup

First set up your python virtual environment.
```
python -m venv .venv
```

Then activate it with:
```
.venv\Scripts\activate.bat      # Windows
. .venv/bin/activate              # Linux
```

Install python dependencies:
```
pip install -r requirements-base.txt
```

Install testing dependencies:
```
pip install -r requirements-test.txt
```

Set app development as True when developing:
```
SET APP_DEVELOPMENT=True         # Windows
export APP_DEVELOPMENT=True      # Linux
$Env:APP_DEVELOPMENT="True"      # Powershell
```

Do your migrations (create your development database):
```
python manage.py migrate
```

Run the django server using:
```
python manage.py runserver
```

## Testing

Ensure you have installed the testing requirements:

```
pip install -r requirements-test.txt
```

Navigate to the folder containing manage.py and run:

```
python manage.py test
```

Ensure all tests pass. This step can also be done using `coverage run` instead of `python`.

If you wish to run only a specific set of tests, specify the _relative path_. All tests that are discovered within that relative path will be run:

```
python manage.py test accounts.tests.views.test_user.AuthenticatedUserViewTest.test_get_user
```

This is of the form `{app}.{path_to_test_file}.{test_file}.{TestClassName}.{UnitTestName}`.

## Code Coverage

In the manage.py folder run:

```
coverage run manage.py test
```

```
coverage report
```

Any files that have untested code will be displayed. If there are none displayed then all _lines of code_ are fully tested, congratulations! Note this does not mean every possible action has been tested (i.e. Auth/No Auth).


## API Spec Generation

The API spec is contained under the docs folder in the project. There will be one yaml file. 

- Any custom responses such as for validation
- Query Parameters
- Authorization Header