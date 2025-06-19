# E2E - PlayWright Tests

We will use playwright for testing e2e and we built below structure for it to be standarized.

```bash
tests
│
├── cases <- all actual tests
│   └── login.spec.ts <- login page tests
├── components <- all components classes and locators
│   └── auth
│       └── login.ts <- login component class and locators
└── core
│   └── auth.setup.ts <- you will add different auth user here
│   └── index.ts <- you will never change this
│   └── helpers <-you will add different data reseter apis here
└── .auth
│   └── {role}-session.json <- session storage for the logged user
└── test-data
│   └── {fileName} <- different test data files
└── config.ts <-  stores environment variables related to test
```

We also have below commands to run different tests

"e2e": "playwright test",
"e2e:ui": "playwright test --ui",
"e2e:debug:chromium": "playwright test --project chromium --headed",
"e2e:debug:firefox": "playwright test --project firefox --headed",

So for you to be able to run them, below example:

```sh
yarn run e2e
yarn run e2e:ui
yarn run e2e:debug:chromium
yarn run e2e:debug:firefox
```

happy testing