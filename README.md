# Playwright Cookiecutter

This is a simple repository that contains the basics to get you started with the base guidelines of testing with playwright.

This is intended for testing End-to-End sites for `angular`, `reactjs` and `vuejs`.

## Getting Started

To be able to use this cookiecutter you need to do few things as follow

### Install Cookiecutter

The simplest way to install cookiecutter is to run your own python virtualenv then install is.
Depending on your environment, you can do either,

-   `virtualenv venv && source venv/bin/activate` if you are using virtualenv
-   `mkvirtualenv cookiecutter` if you are using

After that you can install cookiecutter via the following command:

```bash
pip install cookiecutter
```

### Using The Template

To be able to use the template first you need access to it. Then you can copy the template URL and run the following command:

For `JS`

```bash
cookiecutter git@github.com:Amr-Muhammad/cookiecutter.git -c js
```

For `PYTHON`

```bash
cookiecutter git@github.com:Amr-Muhammad/cookiecutter.git -c python
```

After running the command you will be asked some questions and based on your answers it will generate
new folder called, `tests` and the structure of it is as follows:

```bash
tests
│
├── cases <- all actual tests
│   └── login.ts <- login page tests
├── components <- all components classes and locators
│   └── auth
│       └── login.ts <- login component class and locators
└── core
│   └── auth.setup.ts <- you will add different auth user here
│   └── index.ts <- you will never change this
└── config.ts <- stores environment variables related to test
```
