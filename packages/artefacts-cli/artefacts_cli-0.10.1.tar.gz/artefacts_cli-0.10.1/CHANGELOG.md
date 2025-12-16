# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.10.0] - 2025-11-14

### Added

- Validate project name format in `artefacts config add` command to ensure it includes organization in `org/project` format (#367)

### Changed

- Internal code migration to using a new SDK to the Artefacts API, now following OpenAPI standards (#356)

### Fixed

- Made the JSON metrics file compatible with the `pytest_file` option (#358)

## [0.9.9] - 2025-10-14

### Added

- rosbags will be checked for, and uploaded, when using `run` rather than `launch_test_file` as long as framework is set to `ros2:<version>` (#334)
- Generate unique upload folder for each run and expose it at the `ARTEFACTS_SCENARIO_UPLOAD_DIR` env var (#249)
- CPU and memory statistical information per process run by the CLI. `--show-stats` to get a summary, and `--track-resources` to get CSV time-series data in the dashboard. (#331)
- BETA: artefacts now supports `pytest` as a test framework (whether using regular `pytest` or ros2 `launch_pytest`). Input the path to your pytest file with new `pytest_file:` key. This is a work in progress and so some functionality compared to ros2 `launch_test` maybe missing.  (#336)

## [0.9.8] - 2025-09-18

### Added

- Prompt on `artefacts config add` when the project name differs from any local artefacts.yaml file (#304, #186)
- Detect if new CLI versions are available, and inform you inline (#73)
- The CLI will now parse test results from JUnit XML if one is created from the `run` command. (Not just `ros_testfile`), allowing test results to be correctly displayed on the Artefacts Dashboard. (#322)
- `artefacts hello` can pick the project name from the Artefacts configuration file (#109)
- `artefacts hello` warns if project name argument differs any Artefacts configuration file (#305, #186)
- `launch_test_file` key in `settings` added. Replaces `ros_testfile` when setting the testfile to be used when using the ros2 `launch_test` test framework. (#328)

### Changed

- Determination of testsuite to use is now based on the test framework file chosen in `settings` rather than `framework`. (#328)
- `artefacts hello` does not report any framework in use. This is to avoid confusing situations when configuration file and dashboard get different settings. (#327)

### Fixed

- Key validation to better inform and reject empty strings (#301)
- Wrong error report on some API interaction errors (e.g. `artefacts hello` with invalid API key was cryptic) (#194)

### Deprecated

- `ros_testfile`: Pleasee use `launch_test_file` instead. (#328)

## [0.9.7] - 2025-08-04

### Added

- Upload progress bars now get updated with bytes sent (#148)
- Upload progress bars also apply to post-test uploads to dashboard (#312)

### Fixed

- Uniform job data handling: Remote runs differed and missed configuration on dashboard (#283)
- Runs in container could not detect generated images. This might have been since 0.9.2 🙇

## [0.9.6] - 2025-07-24

### Added

- Nicer reports on SIGINT, and report to the API when needed to update the dashboard (#292)
- Interactions with the Artefacts API get error handling with explanation (#284)

### Fixed

- Automated download of the docker package when Docker Enging available (#290)
- Two bugs on SIGINT, where handling was using values leading to confusing error reports (#93)
- Show Docker errors when Dockerfile contains syntax issues. Errors where masked so far

### Removed

- ROS1 has reached end-of-life in May 2025. This release removes support completely (#274)
- Removed support for legacy code triggered by warp.yaml (#127)

## [0.9.5] - 2025-06-30

### Added

- API calls are automatically retried up to 3 times on server-side 502, 503, 504 errors (#264)
- API calls get short timeout to detect network issues and report ot the user nicely (#264)

### Fixed

- Wrong error handling on `artefacts config add`, resulting in HTML `artefacts.yaml` (#220)
- Correct number of runs in a given job now correctly submitted to the dashboard api (#281)
- Jobs moves onto next run on certain errors which previously terminated the job in run local (#281)

## [0.9.3] - 2025-06-03

### Removed

- Removed unique scenario names for `run-remote` jobs as no longer required by dashboard

## [0.9.2] - 2025-05-27

### Added

- Deeper and tentatively complete localisation of the CLI framework (#262)
- ROS tests can be recorded as "error" rather than just fail or success (#267)

### Fixed

- Compliance with the Artefacts API protocol on reporting common scenario names
  across parameterised runs.

## [0.9.1] - 2025-04-30

### Added

- Runs in container accept and pass options to the underlying container engine (#246)
- Internationalisation of command output and Japanese support (#139)

### Fixed

- Compliance with the Artefacts API protocol on upload/no-upload option (#217)

## [0.8.0] - 2025-04-04

### Added

- Run in containers with only an artefacts.yaml configuration file. No need to
  write a Dockerfile in many standard situations.

### Changed

- New logging messages and format.

### Fixed

- Logging correctly filters between logs for stderr and stdout
- Client now correctly handles rosbags not saved to the top level of a project.
- Fixed error formatting of test error(s).

## [0.7.3] - 2025-03-26

### Fixed

- Handle nested ROS params in the configuration file.

## [0.7.2] - 2025-03-19

### Fixed

- Fixed error handling (bug from misuse of Click's `ClickException`).

### Changed

- Improved error handling and messages.


## [0.7.1] - 2025-03-14

### Added

- Partial CHANGELOG with information on the day we start SemVer and the current
  0.7.0. More detail to come inbetween, but we will focus on the future.

### Changed

- Replace Ruff shield for the original Black one.


## [0.7.0] - 2025-02-25

### Added

- Default upload directory to automatically include output from the Artefacts
  toolkit.

### Changed

- Always rebuild container images before run. These incremental rebuilds avoid
  existing confusion when running an updated code base without rebuilding.
- Separate CD workflow from PyPi publication testing: For reusability and
  direct invocation.


## [0.5.8] - 2024-08-19

### Added

- Beginning of semantic versioning.
- Local metrics errors do not block publication of results.
- Introduction of Black formatting. 

[unreleased]: https://github.com/art-e-fact/artefacts-client/compare/0.9.8...HEAD
[0.9.8]: https://github.com/art-e-fact/artefacts-client/releases/tag/0.9.8
[0.9.7]: https://github.com/art-e-fact/artefacts-client/releases/tag/0.9.7
[0.8.0]: https://github.com/art-e-fact/artefacts-client/releases/tag/0.8.0
[0.7.0]: https://github.com/art-e-fact/artefacts-client/releases/tag/0.7.0
[0.5.8]: https://github.com/art-e-fact/artefacts-client/releases/tag/0.5.8
