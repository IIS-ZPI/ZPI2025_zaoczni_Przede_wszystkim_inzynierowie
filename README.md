## CI/CD Pipeline

This project uses a CI/CD pipeline implemented with **GitHub Actions** to automate testing, quality checks, and the release process.  
The pipeline ensures that every change to the codebase is verified and that only tested versions are released.

---

## Pipeline Triggers

The pipeline is automatically triggered in the following cases:

- push events and pull requests to the `master`, `develop`, and `release` branches,
- pull requests targeting the `master`, `develop`, and `release` branches.

This setup supports a simple branch-based development workflow and enforces quality gates before releasing new versions.

---

## Unit Tests and Code Quality

As part of the continuous integration process, **unit tests are executed automatically** using the `pytest` framework.

During the test stage, the pipeline:
- runs all unit tests,
- measures code coverage for the application modules,
- generates coverage reports in multiple formats:
  - terminal summary,
  - XML report,
  - HTML report.

The HTML coverage report is published as a pipeline artifact and can be downloaded from the GitHub Actions run summary.  
It provides detailed information about tested files, executed lines of code, and overall test coverage.

---

## Release Process

When a **pull request targeting the `release` branch** is successfully validated (all unit tests pass), the pipeline automatically performs the release process.

The release stage includes:
- generating a new version number starting from `2.0.0`,
- creating a Git tag for the new version,
- building a distributable artifact of the application,
- publishing a new GitHub Release with the generated artifact attached.

This ensures that every released version of the application is tested, versioned, and traceable.

---

## Artifact Generation

The project is implemented in Python and provides **two release artifacts**:

### 1. Windows Executable (`.exe`)
For Windows users, the project is released as a **standalone executable (`.exe`)** built using PyInstaller.  
This artifact:
- bundles the application code and all required dependencies,
- does **not** require a Python interpreter to be installed,
- is suitable for direct execution on Windows systems.

### 2. Source Distribution (`.zip`)
A compressed archive (`.zip`) is also provided containing:
- the application source code,
- dependency definitions,
- project documentation.

This artifact is intended for deployment or development in environments where a Python interpreter is available.

---

## NBP Client

**NBPClient** is a Python client for interacting with the **National Bank of Poland (NBP) REST API**.  
It allows you to fetch the latest currency exchange rates or retrieve historical rates over a given date range.  
Responses are mapped into **immutable `ExchangeRateDTO` objects**, ensuring safe and consistent use in the application.

---

## Product Backlog

Project requirements, tasks, and development progress are managed using **Jira**.

The product backlog is available at:

**Jira Product Backlog**  
https://zpi-przede-wszystkim-inz.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog
