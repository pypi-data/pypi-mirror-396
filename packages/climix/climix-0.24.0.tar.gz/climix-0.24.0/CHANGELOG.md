# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security


## [0.24.0] - 2025-12-11

### Added
- Added note on build package name on conda-forge (fixes #394)
- Add assertion error if the input data does not match the requirements (fixes #270)
- Add option to save output in multiple files (fixes #401)

### Changed
- Change pyxdg dependency to platformdirs (fixes #370)
- Update dependencies

### Removed
- Removed numpy<2 from envrionment requirements (fixes #400)
- Remove aux coordinates for period added by climix (fixes #396)

### Fixed
- Update index catalog to only include indices for implemented index functions (fixes #377)
- Fix CannotAddError for already existing auxiliary coordinates (fixes #398)


## [0.23.1] - 2025-07-30

### Added
- Update documentation and parser with --mask-start and --mask-end (fixes #392)

### Changed
- Updated intersphinx_mapping to new format (fixes #393)

### Fixed
- Modified how version string is built in docs/source/conf.py (fixes #358)


## [0.23.0] - 2025-06-23

### Added
- Add start of seasons index functions (fixes #372, fixes #373, fixes #374, fixes #375, fixes #376)
- Added functionality to read parameter_files that mask the data (fixes #385, fixes #386, fixes #384, fixes #338)

### Changed
- Replace inf values with nan values in index functions LastOccurrence and FirstOccurrence (fixes #391)
- Implements gordias reference period (fixes #389)
- Use gordias change units (fixes #380)
- Use gordias filename template (fixes #381)

### Removed
- Remove spell length call function (fixes #326)

### Fixed
- Fixes bug when add a aux coordinate in spell_length index function (fixes #383)
- Build fixes (fixes #387, #388)


## [0.22.0] - 2024-06-17

### Added
- Adds start of spell to spell length index function and tests (fixes #364, fixes #365)
- Release process documentation as do-nothin script (fixes #333)

### Changed
- Updated dependencies (fixes #361)
- Updating srun jobscript and removing mpi script. (fixes #366)

### Removed
- Removed pandas dependency(fixes #357)

### Fixed
- Enable python 3.12 in pyproject.toml (fixes #360)


## [0.21.1] - 2024-03-01

### Fixed
- dependency fixes


## [0.21.0] - 2024-02-21

### Added
- Add gordias connection to climix (fixes #334)

### Changed
- Author and docs update (fixes #343, #fixes #347)

### Removed
- Removed SMHI-extra index definitions (fixes #348)
- Disabled the use of sentry (fixes #349)

### Fixed
- Fix numba compilation error (fixes #346)


## [0.20.0] - 2023-12-12

### Added
- Feature add computational period (Fixes #289)
- Implementation of new index (precip condition and double temperature condition)

### Changed
- Extended documentation CLI, output template description and logo (Fixes #337 #38)
- Fix gsstart, gsend, gsl and add tests (fixes #216, #268)
- Added array_equal function and fixed issues in tests not passing (Fixes #335)
- Updating to clix-meta v0.6.1 (fixes #340)

### Fixed
- Update documentation to clix-meta-0.6.1 (fixes #342)
- Fix to get integration tests configuration file discoverable. (fixes #325)
- Add pandas as dependency (fixes #341)
- Added exception when creating coordinate "year" (fixes #252)


## [0.19.0] - 2023-09-14

### Changed
- Updating clix-meta files to v0.6.0 (fixes #320)
- Update index docs for clix-meta-0.6.0
- Blackify source code (closes #330)

### Fixed
- Fixed cube_diff (fixes #314, fixes #313)
- Fixed CountJointOccurrences not passing unit tests (fixes #305)
- Fixed Percentile and ThresholdedPercentile not passing all unit tests (fixes #310)
- Fixed unit tests for RunningStatistics and ThresholdedRunningStatistics (fixes #307)
- Add unit tests for FirstOccurrence and LastOccurrence (fixes #311)
- Fixes masked array issue with numba (fixes #322)


## [0.18.1] - 2023-04-25

### Changed
- Improve readthedocs config

### Fixed
- Fix packaging (closes #312)


## [0.18.0] - 2023-04-21

### Added
- Reference period defined in Index_definition.yml and command line arg -r/-reference_period (fixes #273)
- Adds global metadata configuration (fixes #36)
- Adds unit tests for index functions(fixes #299)
- Read Clix meta version and add information in cube output attribute (fixes #284)
- Adding integration tests using a subset of indices in NGCD dataset (fixes #275)
- Add Apache-2.0 license (closes #50)
- Create basic documentation (closes #84, #287)

### Changed
- Clix meta update to version 0.5.2 (fixes #306)
- Update build config (Closes #304)


## [0.17.0] - 2023-03-10

### Added
- Index functions for requested indices (fixes #282 #283)
- Functions to parse dates and durations in iso 8601 format (fixes #294)

### Changed
- Replace cube `cell_methods` with `cell_methods` from index definition file (fixes #193)

### Fixed
- Make sure results are realised before assigning to netcdf variable
- Update `spell_kernel` to work on cubes of any dimension


## [0.16.0] - 2023-01-31

### Added

- Added command line argument -f to specify an external metadata file (fixes #228)
- Index functions for CountThresholdedPercentileOccurrences (fixes #197)
- Command line argument for time period (closes #255)
- Enable option to specify annual monthly range (fixes #95)
- Annual single month (fixes #266)

### Changed

- Error message with description of differences between cubes when concatenation fails (fixes #264)
- Updating index_definitions.yml and variables.yml to clix-meta 0.4.1 (fixes #269)

### Fixed

- Rx2day, Rx5day infinite values fix (fixes #260)


## [0.15.0] - 2022-11-16

### Added

- DiurnalTemperatureRange takes reducer as argument to constructor (fixes #187)
- Index function running statistics (closes #86)
- Index function thresholded running statistics (closes #157)
- Index function first spell (closes #245)
- Added debug logging of metadata files (closes #186)

### Changed

- Improve guess output template (fixes #231)
- Updating yaml reader code to match new clix-meta specification (fixes #261)
- Update jobscripts and dependencies (fixes #258)
- Changed logging message levels to be more user-oriented (closes #190)

### Fixed

- Realize coord data before save  (fixes #253)
- Accept all temperature units convertible to Celsius (fixes #250)
- Adjust number of threads per worker if it exceeds number of physical cpus (fixes #215)


## [0.14.0] - 2021-07-28

### Added

- Add pre-commit configuration (closes #223)

### Changed

- Update iris (closes #217)
- Improve slurm integration (closes #236)
- Small technical improvements (closes #237)
- Improve logging in datahandling (closes #238)
- Improve iterative storage (closes #239)
- Improve datahandling documentation (closes #240)
- Blackify source code (closes #241)
- Replace pkg_resources with importlib.metadata for entry points (closes #225)

### Fixed

- Fix handling of seasonal periods that straddle years (fixes #226)
- Fix (dask) meta handling in spell functions (closes #242)
- Fix seasonal period (fixes #243)


## [0.13.2] - 2021-05-01

### Changed

- Remove editor (closes #207)

### Fixed

- Fix multi variable indices (fixes #208)
- Fix percentiles (fixes #205)
- Fix comparison operators in CountPercentileOccurrences (fixes #224)
- Pin iris version to <3 (closes #218)
- Pin iris in environment.yml (closes #220)


## [0.13.1] - 2020-10-21

### Fixed

- Rename percentile_occurrence index function (fixes #202)


## [0.13.0] - 2020-10-19

### Added

- Add scalar mean reducer (fixes #184)
- Add flag parameter type to index function metadata (closes #188)
- Percentile based indices (closes #196)
- Add hpc schedulers (closes #200)

### Changed

- Improve spell length implementation (closes #129)
- Improve postprocessing (closes #180)
- Add client passing to increase flexibility in processing (closes #181)
- Improve sliced mode and saving (closes #182)
- Improve spell length calculation to deal with period boundary-crossing spells (closes #183)
- Make spell fusing across periods optional (closes #74)
- Change fusing behavior to consider spells in all affected periods (closes #189)
- Detect tty for non-interactive logging output (closes #185)
- Account for hyperthreading in LocalCluster scheduler

### Removed

- Removed obsolete legacy directory
- Removed obsolete legacy branch
- Remove six (closes #160)


## [0.12.0] - 2020-02-20

### Added

- Added master table as submodule (closes #169)
- Added the following index function
  - extreme temperature range, etr (closes #166)
  - diurnal temperature range (closes #153)
  - interday diurnal temperature range (closes #154)
  - percentile (closes #80)
  - thresholded percentile (closes #85)
- Added changelog utility scripts (closes #172)

### Changed

- Update metadata to master table version 0.1.0 (closes #171)

### Fixed

- Remove formatting for all `standard_name`s (fixes #167)


## [0.11.0] - 2020-02-12

### Added

- Add handling of aliased input variables (closes #155)
- Multiple inputs index functions (closes #82)
- Add count_level_crossings index function (closes #151)
- Add nzero index (closes #146)

### Changed

- Improve input variables (closes #152)
- Improved logging setup (closes #143)
- Update editor to deal with new master table (closes #161)
- Improved metadata error reporting (closes #162)
- Update metadata handling (closed #163)
- Update metadata (closes #164)


## [0.10.0] - 2019-11-21

### Added

- Handle negative parameter values (closes #117)
- Add single-threaded dask setup (closes #125)
- Add unified configuration handling (closes #19)
- Improve reporting of index problems (closes #128)
- Add error detection and reporting to climix-editor (closes #130)
- Store parameters as scalar coords (closes #73)
- Add changelog (closes #131)
- Index function statistics (closes #79)
- Index function temperature_sum (closes #81)

### Changed

- Improve help (closes #103)
- Cleanup dataclasses based metadata handling (closes #126)
- Deal with missing long_name in quantity parameters (closes #127)
- Index functions refactoring (closes #137)
- Add conversion of dtype to threshold handling (fixes #136)
- Reorganize index metadata (closes #133)


## [0.9.0] - 2019-11-04

### Added

- Add index templating along with editor component
  for new table format (closes #70, closes #76)
- Add command line option to deactivate sentry (closes #119)
- Add pylama config and improve code style (closes #120)

### Changed

- Adapt editor to new index function column (closes #123)

### Fixed

- Fix ready detection in editor (closes #122)
- Fix dask setup (closes #124)


## [0.8.1] - 2019-10-11

### Added

- Add sentry tracker to main.py (closes #51)

### Changed

- Update dependency information with minimal versions (closes #114)

### Fixed

- Fix typo


## [0.8.0] - 2019-09-26

### Added

- Add basic logging (closes #108)
- Add index last_spring_frost (closes #88)
- Add index function last_occurrence (closes #97)

### Changed

- Simplify string formatting (closes #109)
- Improve dask setup (closes #110, closes #26)
- Improve input data preparation (closes #111)
- Improved saving and sliced mode (closes #112, closes #113)

### Fixed

- Fix SpellLength (closes #104)
- Fix Monthly period (closes #106)
- Fix and refactor change_pr_units (closes #107)


## [0.7.1] - 2019-09-26

### Fixed

- Fix SpellLength (closes #104)
- Fix Monthly period (closes #106)
- Fix and refactor change_pr_units (closes #107)


## [0.7.0] - 2019-07-03

### Added

- Add post processing hook for index functions (closes #100)
- Add index first_autumn_frost (closes #89)
- Add index function first_occurrence


## [0.6.0] - 2019-07-03

### Added

- Add climpact2 reference dataset (closes #33)
- Add index sdii (closes #7)


## [0.5.1] - 2019-07-02

### Fixed

- Fix bug in CountOccurences (fixes #71)
- Accept input data without creation_date and tracking_id (fixes #87)
- Fix index function spell_length (fixes #91)
- Fix typo: CountOccurrences (closes #90)


## [0.5.0] - 2019-05-29

### Added

- Templated index generation (closes #47)
- Add index function thresholded_statistics (closes #68)

### Changed

- Move complete lazy and non-lazy calculations into index functions (closes #58)
- Changed cdd to standard definition (fixes #5)

### Fixed

- Fixed infrastructure for output unit handling (fixes #66)
- Fix output unit handling by moving it to post_process (fixes #67)


## [0.4.0] - 2019-05-17

### Added

- Add support for proposed_standard_name (see #45, closes #48)
- Add `count_occurrences` index function (closes #54)
- Add common operators (closes #55)
- Add period label as frequency attribute to output (closes #17)
- Add frequency to output filename template (closes #35)
- Add r10mm index (closes #6)
- Add index cwd (closes #42)
- Add index su (closes #49)

### Removed

- Remove unused reducer from count_occurrences index function (closes #56)

### Fixed

- Fix formatting errors in r10mm definition (fixes #59)
- Fix cwd operator (fixes #44)


## [0.3.1] - 2019-05-13

### Fixed

- Fix bug in prepare (fixes #41)


## [0.3.0] - 2019-05-10

### Added

- Index from metadata (closes #25)
- Add sliced_mode to avoid memory problems (closes #30)
- Add annual and monthly periods (closes #28)
- Add index_function infrastructure (closes #27)
- Add transformation of parameters via index_function prepare (closes #31)

### Changed

- Move coord categorization to period class (closes #29)
- Detect precipitation in input data, not threshold parameter (closes #39)

### Fixed

- Fix aggregator bug (fixes #34)


## [0.2.0] - 2019-05-06

### Added

- Add util functions (closes #22)
- Add better CLI (closes #24)

### Changed

- Improv cube_diffs function (closes #23)

### Fixed

- Fix off-by-one bug in Season (fixes #13)


## [0.1.0] - 2019-04-24

### Added

- First aggregator version
- Added .gitignore file.
- Added timing to output.
- Added SLURM cluster ability from dask-jobqueue.
- Add python packaging
- Add documentation setup using sphinx (closes #20)

### Changed

- Cleaned up aggregator, added metadata handling.
- Cleanup legacy part.
- Improved directory structure.

### Removed

- Removed obsolete version.

[unreleased]: https://git.smhi.se/climix/climix/compare/v0.24.0...HEAD
[0.24.0]: https://git.smhi.se/climix/climix/compare/v0.23.1...v0.24.0
[0.23.1]: https://git.smhi.se/climix/climix/compare/v0.23.0...v0.23.1
[0.23.0]: https://git.smhi.se/climix/climix/compare/v0.22.0...v0.23.0
[0.22.0]: https://git.smhi.se/climix/climix/compare/v0.21.1...v0.22.0
[0.21.1]: https://git.smhi.se/climix/climix/compare/v0.21.0...v0.21.1
[0.21.0]: https://git.smhi.se/climix/climix/compare/v0.20.0...v0.21.0
[0.20.0]: https://git.smhi.se/climix/climix/compare/v0.19.0...v0.20.0
[0.19.0]: https://git.smhi.se/climix/climix/compare/v0.18.1...v0.19.0
[0.18.1]: https://git.smhi.se/climix/climix/compare/v0.18.0...v0.18.1
[0.18.0]: https://git.smhi.se/climix/climix/compare/0.17.0...v0.18.0
[0.17.0]: https://git.smhi.se/climix/climix/compare/0.16.0...0.17.0
[0.16.0]: https://git.smhi.se/climix/climix/compare/0.15.0...0.16.0
[0.15.0]: https://git.smhi.se/climix/climix/compare/0.14.0...0.15.0
[0.14.0]: https://git.smhi.se/climix/climix/compare/0.13.2...0.14.0
[0.13.2]: https://git.smhi.se/climix/climix/compare/0.13.1...0.13.2
[0.13.1]: https://git.smhi.se/climix/climix/compare/0.13.0...0.13.1
[0.13.0]: https://git.smhi.se/climix/climix/compare/0.12.0...0.13.0
[0.12.0]: https://git.smhi.se/climix/climix/compare/0.11.0...0.12.0
[0.11.0]: https://git.smhi.se/climix/climix/compare/0.10.0...0.11.0
[0.10.0]: https://git.smhi.se/climix/climix/compare/0.9.0...0.10.0
[0.9.0]: https://git.smhi.se/climix/climix/compare/0.8.0...0.9.0
[0.8.1]: https://git.smhi.se/climix/climix/compare/0.8.0...0.8.1
[0.8.0]: https://git.smhi.se/climix/climix/compare/0.7.0...0.8.0
[0.7.1]: https://git.smhi.se/climix/climix/compare/0.7.0...0.7.1
[0.7.0]: https://git.smhi.se/climix/climix/compare/0.6.0...0.7.0
[0.6.0]: https://git.smhi.se/climix/climix/compare/0.5.1...0.6.0
[0.5.1]: https://git.smhi.se/climix/climix/compare/0.5.0...0.5.1
[0.5.0]: https://git.smhi.se/climix/climix/compare/0.4.0...0.5.0
[0.4.0]: https://git.smhi.se/climix/climix/compare/0.3.1...0.4.0
[0.3.1]: https://git.smhi.se/climix/climix/compare/0.3.0...0.3.1
[0.3.0]: https://git.smhi.se/climix/climix/compare/0.2.0...0.3.0
[0.2.0]: https://git.smhi.se/climix/climix/compare/0.1.0...0.2.0
[0.1.0]: https://git.smhi.se/climix/climix/-/tags/0.1.0
