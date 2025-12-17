# Contributing to `waft`
In order to establish consistency among contributors and aid reviewers in evaluating contributions, below we detail standards to serve these ends.
## Developer Tool Chain Resources
It is imperative that a prospective contributor familiarize themselves with the tool chain and technological stack employed
during the development of this project. The proceeding is a list of these tools/frameworks/libraries, a brief commentary on
their usage in relation to this project, and links to their documentation:
- [Python](https://docs.python.org/3.13/): Python is a dynamic programming language with various advantages that make it a good choice for the development of our application, primarily its robust ecosystem of well maintained libraries. Additionally, most of the core team posses at least intermediate facility with it. While Python 3.14 is stable at the time of writing, [3.13](https://docs.python.org/3/whatsnew/3.13.html) was chosen as it is the first version to offer the ability to disable the [GIL](https://wiki.python.org/moin/GlobalInterpreterLock).
- [Mamba](https://mamba.readthedocs.io/en/latest/index.html): When attempting to develop in Python, it is important to keep package and library versions consistent across machines, for which [environment](https://docs.python.org/3/library/venv.html) managers are helpful.
    - [Textual](https://textual.textualize.io/): Textual is a Python framework that allows us to create a textual user interface using pre-made widget components, with great asynchronous support. Additionally, applications developed with Textual are rather readily converted into websites, furthering the accessibility of our application.
    - [pudb](https://documen.tician.de/pudb/): A great and versatile step-by-step terminal debugger.
    - [Black](https://black.readthedocs.io/en/stable/): `black` is a code formatter that adheres to the Pythonic standard set out in [PEP 8](https://peps.python.org/pep-0008/).
    - [flake8](https://flake8.pycqa.org/en/latest/): A style guide enforcement tool combining `pyflakes`, `pycodestyle`, and `mccabe` to flag both style and complexity issues.
    - [pylint](https://pylint.readthedocs.io/en/latest/): Performs static code analysis to detect logic errors, unused variables, and code smells.
    - [mypy](https://mypy-lang.org/): `mypy` allows us to check for type consistency, letting us catch a whole swath of tricky runtime errors.
    - [pytest](https://docs.pytest.org/en/stable/): Python’s most popular testing framework, providing fixtures, assertions, and plugin support for clean test design.
    - [MKDocs](https://www.mkdocs.org/): A static website generator that creates documentation from [Markdown](https://www.markdownguide.org/) source files.
    - [mkdocstrings](https://mkdocstrings.github.io/): An extension of MKDocs' capabilities, allowing us to collate inline documentation from Python source files directly.
    - [Coverage.py](https://coverage.readthedocs.io/en/latest/): Measures test coverage and produces terminal and HTML reports, helping track which parts of the codebase are exercised by tests.
    - [interrogate](https://interrogate.readthedocs.io/): Calculates documentation coverage, ensuring that functions, classes, and modules include appropriate docstrings.
- [GitHub Actions](https://docs.github.com/en/actions): Actions workflows allow us to automate pull requests, code review tasks, deployments, documentation generation, etc. They are written in [YAML](https://yaml.org/).
## Opening an Issue
All features, enhancements, and bug reports **must** begin as a [Github Issue](https://docs.github.com/en/issues) submitted through our [project board](https://github.com/users/me11203sci/projects/3/views/1), in order to ensure that progress is visible and so and that work items can be prioritized and assigned efficiently. The steps for doing so are as follows:
1. Begin by checking that a relevant issue does not already exist.
1. Make sure to provide it with a clear and descriptive title.
1. Select the appropriate label for your issue. Features/enhancements **must** employ the User Story template; likewise for bug reports, use the Bug Report template. For documentation issues, the description may be left blank.
1. Give it an appropriate priority level to ensure that more critical issues are addressed expediently.
1. Estimate the number of story points according to the following table:
    |Points|Meaning|Example|
    |:----:|:-----:|:-----:|
    |1|Trivial change|[]()|
    |2|Small task|[#19](https://github.com/users/me11203sci/projects/3?pane=issue&itemId=134884256&issue=me11203sci%7Cwiki-application-for-tunes%7C19)|
    |3|Moderate|[#25](https://github.com/users/me11203sci/projects/3/views/1?pane=issue&itemId=135011984&issue=me11203sci%7Cwiki-application-for-tunes%7C25)|
    |5|Complex|[#27](https://github.com/users/me11203sci/projects/3/views/1?pane=issue&itemId=135014480&issue=me11203sci%7Cwiki-application-for-tunes%7C27)|
    |8|Large feature|[#18](https://github.com/users/me11203sci/projects/3/views/1?pane=issue&itemId=134795797&issue=me11203sci%7Cwiki-application-for-tunes%7C18)|
    |13+|Too large|[#23](https://github.com/users/me11203sci/projects/3/views/1?pane=issue&itemId=134888194&issue=me11203sci%7Cwiki-application-for-tunes%7C23)|
1. Assign the issue to yourself if you intend to work on the issue; otherwise leave it unassigned for triage.

> [!NOTE]
> It may be necessary to take a large issue and repeat the issue creation process until it is broken up into more manageable tasks. Most issues are ideally size once they correspond to at most a couple unit tests.

After this, proceed to create a local working branch title composed of the your last name (lowercase) and a brief description of the issue you are working on (in [Pascal Case](https://wiki.c2.com/?PascalCase)), for example `dennison/SpotifyAPISearch`.
## Code Style Guide
To maintain consistency, readability, and long-term maintainability across the codebase, contributors are expected to follow the coding principles stated here.

`waft` adopts a hybrid programming paradigm. Textual adheres to [object oriented programming](https://en.wikipedia.org/wiki/Object-oriented_programming) principles, as components and widgets lend themselves well to encapsulation. By contrast, we otherwise implement application logic and data transformation using [functional programming](https://en.wikipedia.org/wiki/Functional_programming) and [data oriented programming](https://en.wikipedia.org/wiki/Data-oriented_design) principles respectively.

We advise contributors to follow established design and architectural conventions, this can primarily be seen through the aforementioned used of the Model-Update-View utilized within the application logic. For other aspects of the project, it is advisable to refer to the [Refactoring Guru](https://refactoring.guru/design-patterns) online guide in order to reference design patterns and their explanations.

Code quality is maintained through a suite of automated tools integrated into our development workflow. All functions and classes must include explicit type hints validated with `mypy`, ensuring type consistency and early detection of logic errors. Source files need to be formatted with `black`, which enforces a uniform code style across the repository. Before opening a pull request, contributors must run `flake8` and `pylint` to identify unused imports, complexity issues, and potential code smells.

Tests should be written with `pytest` and measured using `Coverage.py` to ensure that new code maintains or improves overall coverage thresholds. In parallel, all public modules, classes, and functions must include clear and descriptive docstrings following the conventions laid out by the [numpydoc](https://numpydoc.readthedocs.io/en/latest/format.html#overview) convention. Documentation coverage is tracked with `interrogate`, ensuring that the codebase remains both verifiable and intelligible.

All of these checks are automated in the CI pipeline to ensure that every merge meets consistent standards of clarity, maintainability, and correctness.
## Commit Style Guide
For this project, we have attempted to follow the [guidance](https://cbea.ms/git-commit/) outlined by [cbeams](https://cbea.ms/author/cbeams/), which can be summarized in the following 7 rules:
1. Separate subject from body with a blank line.
2. Limit the subject line to 50 characters.
3. Capitalize the subject line.
4. Do not end the subject line with a period.
5. Use the [imperative mood](https://en.wikipedia.org/wiki/Imperative_mood) in the subject line.
6. Wrap the body at 72 characters.
7. Use the body to explain *what* the commit accomplishes and *why*.
## Pull Request Review
Once you are ready to merge your contributions into the codebase, begin a pull request to have a core team member review your contribution. As outlined in [this guide from Google](https://google.github.io/eng-practices/review/reviewer/standard.html), reviewers should rely on metrics (for this we employ GitHub Actions to run the aforementioned code analysis tools) and design principles over preferences. The following checklist is provided for your convenience:
- [ ] Begin by verifying that the branch name adheres to the standard: `[lastname]/[PascalCaseDescription]`.
- [ ] Ensure that all commits follow the commit style guide.
- [ ] Verify error handling and logging are appropriate and consistent with existing conventions.
- [ ] Confirm that code passes static analysis (using `black`, `flake8`, `pylint`, `mypy`.)
- [ ] Check that tests pass and coverage thresholds are maintained (using `pytest` and `Coverage.py`.)
- [ ] Ensure that documentation coverage remains above the acceptable thresholds (using `interrogate`.) Review these documentation updates, ensuring docstrings are consistent, accurate, and clear.
- [ ] Assess whether naming, readability, and modularity meet project standards.
- [ ] Evaluate whether the code adheres to the design principles stated above.
- [ ] If applicable, evaluate whether the related issue's acceptance criteria are met.

Should one deem that accepting the pull request under evaluation would be detrimental to the health of the codebase, propose specific comments that instruct the author of the contribution on how they could go about addressing your concerns. Once code receives the manual approval of at least one other core team member, it is acceptable to merge onto the `master` branch.
## Core Development Team
**User Interface Design Lead:** [Melesio Albavera](https://github.com/me11203sci/)

**Back-End Development Lead:** [Luke Dennison](https://github.com/LukeDennison/)

**Application Logic Lead:** [Eli Wetzel](https://github.com/ejw255/)

**Emotional Support Expert (External Consultant):** [ChatGPT](https://chatgpt.com/)
