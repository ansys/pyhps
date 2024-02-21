# CHANGELOG

## [0.7.0](https://github.com/ansys/pyhps/releases/tag/v0.7.0) - February 21 2024

### Added
- feat: needed permissions for junit action
- feat: update license start year (#334)
- Add codecov to the repository (#339)

### Fixed
- fix: followup tech review (#300)
- fix: workflow permissions (#301)
- fix: github output instead of env var (#303)
- fix: outputs
- Fix coverage (#307)
- fix: stage dependencies (#313)
- fix: solve badges (#340)

### Changed
- Technical review [#273](https://github.com/ansys/pyhps/pull/273)
- Replace unittest with pytest (#298)
- cicd: proposing different action (#302)
- Cleanup workflows (#306)
- Update RMS models (#308)
- Additional cleanup (#312)
- Update tests for LS-DYNA example (#276)
- More docs and url renaming (#316)
- Update README.rst (#317)
- DCS migration guide (#314)
- Adjust schemas docstrings (#318)
- Expose task work dir (#320)
- Update fluent nozzle example (#319)
- Rework Doc API Reference (#321)
- Remove issue templates (#327)
- docs: installation steps (#336)
- Post tech-review updates (#338)

### Dependencies
- Bump ansys-sphinx-theme from 0.13.1 to 0.13.2 (#297)
- Bump docker/login-action from 2 to 3 (#292)
- Bump dawidd6/action-download-artifact from 2 to 3 (#290)
- Bump peter-evans/create-or-update-comment from 2 to 4 (#295)
- Bump actions/checkout from 3 to 4 (#293)
- Bump sphinxnotes-strike from 1.2 to 1.2.1 (#296)
- Bump sphinx-autodoc-typehints from 1.25.2 to 1.25.3 (#291)
- Bump actions/setup-python from 4 to 5 (#310)
- Bump mikepenz/action-junit-report from 3 to 4 (#309)
- Bump ansys-sphinx-theme from 0.13.2 to 0.13.4 (#324)
- Bump twine from 4.0.2 to 5.0.0 (#323)
- Bump sphinx-autodoc-typehints from 1.25.3 to 2.0.0 (#325)
- Bump pytest from 8.0.0 to 8.0.1 (#328)
- Bump ansys-sphinx-theme from 0.13.4 to 0.14.0 (#330)
- Bump coverage from 7.4.1 to 7.4.2 (#337)

## [0.6.0](https://github.com/ansys/pyhps/releases/tag/v0.6.0) - January 31 2024

### Added
- Add license headers to files [#270](https://github.com/ansys/pyhps/pull/270)

### Fixed
- Fix small typo in Objects vs Dictionaries [#259](https://github.com/ansys/pyhps/pull/259)
- Improve type checking for create, update and delete methods [#271](https://github.com/ansys/pyhps/pull/271)
- Improvements from testing session [#275](https://github.com/ansys/pyhps/pull/275)

### Changed
- Rename to PyHPS [#258](https://github.com/ansys/pyhps/pull/258)
- More renaming [#260](https://github.com/ansys/pyhps/pull/260)
- Update RMS models and API [#262](https://github.com/ansys/pyhps/pull/262)
- Overall doc edit for public release [#278](https://github.com/ansys/pyhps/pull/268)

### Dependencies
- Bump apispec from 6.3.0 to 6.3.1 in /requirements [#264](https://github.com/ansys/pyhps/pull/264)
- Bump pytest from 7.4.3 to 7.4.4 in /requirements [#266](https://github.com/ansys/pyhps/pull/266)
- Update add-license-headers version [#277](https://github.com/ansys/pyhps/pull/277)

## [0.5.0](https://github.com/ansys/pyhps/releases/tag/v0.5.0) - December 14 2023

### Added
* Expose the resource management service (RMS) API by @FedericoNegri in #247
* Add missing RMS api doc file by @FedericoNegri in #250
* Add wheel asset to release by @FedericoNegri in #255

### Fixed
* Fix download of file when the evaluation path contains a subdir by @FedericoNegri in #254
* Fix task def property by @wehrler in #257

### Changed
* Update nightly workflow by @FedericoNegri in #256

### Dependencies 
* Bump datamodel-code-generator from 0.24.1 to 0.25.1 in /requirements by @dependabot in #249

## [0.4.0](https://github.com/ansys/pyhps/releases/tag/v0.4.0) - November 17 2023

### Added
* Add HPC resources by @wehrler in #186
* Add PR, bug and feature template by @sashankh01 in #179
* Expose SSL certificates verification by @FedericoNegri in #235
* Create File resource with a file-like object by @FedericoNegri in #238

### Fixed
* Jnovak/client refresh failure by @Buzz1167 in #194
* Fix output files and parameter ids in the success criteria by @FedericoNegri in #234
* Fix marshmallow warnings by @FedericoNegri in #239

### Changed
* Update schemas and resources by @FedericoNegri in #196
* Update tests requiring the auth api by @FedericoNegri in #201
* Update github workflows by @FedericoNegri in #220
* Update Python and dependencies versions by @FedericoNegri in #228
* Remove unnecessary files from wheel by @FedericoNegri in #237
* Update examples to optionally use the official execution scripts by @saimanikant in #240

### Dependencies
* Bump pytest from 7.3.2 to 7.4.3 in /requirements by @dependabot in #192, #232
* Bump docs requirements by @FedericoNegri in #245

## [0.3.0](https://github.com/ansys/pyhps/releases/tag/v0.3.0) - June 29 2023

### Added
* Add build_info to evaluator's schema by @FedericoNegri in #190
* Expose created/modified by by @FedericoNegri in #189

### Changed
* Rename external version by @FedericoNegri in #184
* Rework auth api by @FedericoNegri in #185
* Bump default Ansys apps version by @FedericoNegri in #187

### Dependencies
* Bump ``ansys-sphinx-theme`` from 0.9.8 to 0.9.9 in /requirements by @dependabot in #173
* Bump ``pytest`` from 7.3.1 to 7.3.2 in /requirements by @dependabot in #188
* Bump ``pytest-cov`` from 4.0.0 to 4.1.0 in /requirements by @dependabot in #183

## [0.2.0](https://github.com/ansys/pyhps/releases/tag/v0.2.0) - June 6 2023

### Added
* Objects copy by @FedericoNegri in #181

### Fixed
* Fix test: task files by @FedericoNegri in #174

### Changed
* Update ci_cd.yml by @FedericoNegri in #175
* Update nightly build by @FedericoNegri in #176
* Update ci/cd by @FedericoNegri in #178
* Adjust schemas to match jms and evaluator by @wehrler in #182
* Remove file storage from project schema by @wehrler in #160

## [0.1.0](https://github.com/ansys/pyhps/releases/tag/v0.1.0) - May 9 2023

### Added

* Add missing fields for app template handling by @nezgrath in https://github.com/pyansys/pyrep/pull/14
* Okoenig/exec script examples by @ojkoenig in https://github.com/pyansys/pyrep/pull/18
* Add publish step to private pypi. by @jonathanzopes in https://github.com/pyansys/pyrep/pull/20
* Add log messages in execution scripts by @ojkoenig in https://github.com/pyansys/pyrep/pull/27
* Add use_execution_script to pyrep by @ojkoenig in https://github.com/pyansys/pyrep/pull/33
* Add new examples + docstring updates by @FedericoNegri in https://github.com/pyansys/pyrep/pull/35
* Add version as a cmd line argument in the examples by @FedericoNegri in https://github.com/pyansys/pyrep/pull/71
* Add nightly build and make CI run faster by @FedericoNegri in https://github.com/pyansys/pyrep/pull/85
* Add task custom_data field by @FedericoNegri in https://github.com/pyansys/pyrep/pull/143
* Add release job to ci/cd by @FedericoNegri in https://github.com/pyansys/pyrep/pull/172
* Common Client and separate API objects by @FedericoNegri in https://github.com/pyansys/pyrep/pull/28
* Set REP server for CI tests by @FedericoNegri in https://github.com/pyansys/pyrep/pull/39
* Include examples in the doc by @FedericoNegri in https://github.com/pyansys/pyrep/pull/45
* Auto generate code for resource objects by @FedericoNegri in https://github.com/pyansys/pyrep/pull/42
* Fluent example by @FedericoNegri in https://github.com/pyansys/pyrep/pull/46
* Separate tests by @FedericoNegri in https://github.com/pyansys/pyrep/pull/49
* Davel/fluent example by @davel94 in https://github.com/pyansys/pyrep/pull/52
* CFX example by @davel94 in https://github.com/pyansys/pyrep/pull/55
* doc for fluent nozzle and cfx examples by @davel94 in https://github.com/pyansys/pyrep/pull/58
* get_project_by_name in mapdl_motorbike_frame example by @saimanikant in https://github.com/pyansys/pyrep/pull/65
* Don't assume projects exists on server for tests by @FedericoNegri in https://github.com/pyansys/pyrep/pull/86
* Test task definition fields by @FedericoNegri in https://github.com/pyansys/pyrep/pull/92
* Auto-generate __init__ arguments for resources by @FedericoNegri in https://github.com/pyansys/pyrep/pull/93
* Correct dependabot labels by @nezgrath in https://github.com/pyansys/pyrep/pull/101
* Task definition template permissions by @FedericoNegri in https://github.com/pyansys/pyrep/pull/100
* Sort File System Rest Gateway by ascending priority by @FedericoNegri in https://github.com/pyansys/pyrep/pull/112
* Test against local REP deployment by @FedericoNegri in https://github.com/pyansys/pyrep/pull/127
* Verify that a user can query newly created templates by @FedericoNegri in https://github.com/pyansys/pyrep/pull/118
* Enable multi-version documentation by @greschd in https://github.com/pyansys/pyrep/pull/130
* Run unit tests in nightly build against local deployment by @FedericoNegri in https://github.com/pyansys/pyrep/pull/132
* Clean up old/unused files by @FedericoNegri in https://github.com/pyansys/pyrep/pull/133
* Expose distributed flag in the task definition and template by @FedericoNegri in https://github.com/pyansys/pyrep/pull/134
* Expose argument to control the default for the `fields="all"` query parameter by @FedericoNegri in https://github.com/pyansys/pyrep/pull/150
* Helper function to copy default execution scripts by @FedericoNegri in https://github.com/pyansys/pyrep/pull/154
* Ansys org rename by @FedericoNegri in https://github.com/pyansys/pyrep/pull/170
* Expose sync_jobs and deprecate _sync_jobs by @FedericoNegri in https://github.com/pyansys/pyrep/pull/171

### Fixed

* Fix mapdl_motorbike_frame examples. To be continued by @ojkoenig in https://github.com/pyansys/pyrep/pull/5
* Okoenig/fix examples by @ojkoenig in https://github.com/pyansys/pyrep/pull/6
* Okoenig/fix examples by @ojkoenig in https://github.com/pyansys/pyrep/pull/8
* Minor fix by @ojkoenig in https://github.com/pyansys/pyrep/pull/9
* Minor fix for the example as reported by Sorin by @ojkoenig in https://github.com/pyansys/pyrep/pull/12
* Adjust replace rules by @nezgrath in https://github.com/pyansys/pyrep/pull/13
* Small fix for task definition schema. execution_script_id is optional by @ojkoenig in https://github.com/pyansys/pyrep/pull/17
* Pass env correctly by @ojkoenig in https://github.com/pyansys/pyrep/pull/19
* Jzopes/fix code style by @jonathanzopes in https://github.com/pyansys/pyrep/pull/22
* okoenig/fix tests by @ojkoenig in https://github.com/pyansys/pyrep/pull/24
* Fix doc build by @FedericoNegri in https://github.com/pyansys/pyrep/pull/111
* Fix api update calls by @FedericoNegri in https://github.com/pyansys/pyrep/pull/126

### Changed

* Change required_output_parameters to required_output_parameter_ids by @nezgrath in https://github.com/pyansys/pyrep/pull/2
* Updating more examples by @ojkoenig in https://github.com/pyansys/pyrep/pull/7
* Disable pydocstyle for now by @ojkoenig in https://github.com/pyansys/pyrep/pull/11
* Update doc build step. by @jonathanzopes in https://github.com/pyansys/pyrep/pull/21
* Minor update for exec scripts by @ojkoenig in https://github.com/pyansys/pyrep/pull/23
* Doc update + get_project_by_name and pretty print by @FedericoNegri in https://github.com/pyansys/pyrep/pull/36
* Update task definition templates + doc improvements by @FedericoNegri in https://github.com/pyansys/pyrep/pull/38
* Update app names by @FedericoNegri in https://github.com/pyansys/pyrep/pull/53
* Update url of testing server by @FedericoNegri in https://github.com/pyansys/pyrep/pull/59
* Schema and resource generation updates by @FedericoNegri in https://github.com/pyansys/pyrep/pull/57
* Update test server credentials by @FedericoNegri in https://github.com/pyansys/pyrep/pull/75
* Expose update of evaluator configuration by @FedericoNegri in https://github.com/pyansys/pyrep/pull/137
* Update dependencies by @FedericoNegri in https://github.com/pyansys/pyrep/pull/145
* Update dependencies by @FedericoNegri in https://github.com/pyansys/pyrep/pull/162
* Update project copy and evaluator's schema by @FedericoNegri in https://github.com/pyansys/pyrep/pull/165
* Change source import for flake8 by @RobPasMue in https://github.com/pyansys/pyrep/pull/88
* changes to exec scripts for templates.   by @davel94 in https://github.com/pyansys/pyrep/pull/80
* Specify python-keycloak<=2.12.0 to avoid breaking changes with newer releases by @FedericoNegri in https://github.com/pyansys/pyrep/pull/141
* Re-enable the Auth API by @FedericoNegri in https://github.com/pyansys/pyrep/pull/32
* Adjust package name to ansys-rep-client by @FedericoNegri in https://github.com/pyansys/pyrep/pull/138
* Improve type annotations and APIs doc by @FedericoNegri in https://github.com/pyansys/pyrep/pull/47

### Dependencies
* Bump ``sphinx`` from 5.0.2 to 0.10.0 in /requirements by @dependabot in ([#4](https://github.com/pyansys/pyrep/pull/4), [#73](https://github.com/pyansys/pyrep/pull/73), [#109](https://github.com/pyansys/pyrep/pull/109))
* Bump ``ansys-sphinx-theme`` from 0.4.2 to 0.8.2 in /requirements by @dependabot in ([#16](https://github.com/pyansys/pyrep/pull/16), [#25](https://github.com/pyansys/pyrep/pull/25), [#37](https://github.com/pyansys/pyrep/pull/37), [#91](https://github.com/pyansys/pyrep/pull/91), [#98](https://github.com/pyansys/pyrep/pull/98), [#122](https://github.com/pyansys/pyrep/pull/122), [#129](https://github.com/pyansys/pyrep/pull/129))
* Bump ``sphinxnotes-strike`` from 1.1 to 1.2 in /requirements by @dependabot in https://github.com/pyansys/pyrep/pull/34
* Bump ``pytest`` from 7.1.2 to 7.2.1 in /requirements by @dependabot in https://github.com/pyansys/pyrep/pull/44, https://github.com/pyansys/pyrep/pull/77, https://github.com/pyansys/pyrep/pull/113
* Bump ``sphinx-autodoc-typehints`` from 1.18.1 to 1.22 in /requirements by @dependabot in ([#54](https://github.com/pyansys/pyrep/pull/54), [#108](https://github.com/pyansys/pyrep/pull/108), [#123](https://github.com/pyansys/pyrep/pull/123), [#124](https://github.com/pyansys/pyrep/pull/124), [#128](https://github.com/pyansys/pyrep/pull/128)
* Bump dependencies version by @FedericoNegri in https://github.com/pyansys/pyrep/pull/72
* Bump ``apispec`` from 5.2.2 to 6.0.2 in /requirements by @dependabot in https://github.com/pyansys/pyrep/pull/74, https://github.com/pyansys/pyrep/pull/87
* Bump versions in requirements by @FedericoNegri in https://github.com/pyansys/pyrep/pull/84
* Bump ``sphinx-copybutton`` from 0.5 to 0.5.1 in /requirements by @dependabot in https://github.com/pyansys/pyrep/pull/89
* Bump ``sphinxcontrib-httpdomain`` from 1.8.0 to 1.8.1 in /requirements by @dependabot in https://github.com/pyansys/pyrep/pull/90
* Bump ``twine`` from 4.0.1 to 4.0.2 in /requirements by @dependabot in https://github.com/pyansys/pyrep/pull/95
* Bump ``build`` from 0.9.0 to 0.10.0 in /requirements by @dependabot in https://github.com/pyansys/pyrep/pull/110
* Bump ``sphinxcontrib-globalsubs`` from 0.1.0 to 0.1.1 in /requirements by @dependabot in https://github.com/pyansys/pyrep/pull/115
