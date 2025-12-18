# Kognic Base Clients

Python 3 library for providing a base clients for interacting with the Kognic platform

# Changelog

All notable changes to this library will be documented in this file

## [2.4.0] - 2025-04-28

- Adds a patch method

## [2.3.4] - 2024-02-27

- Rework timeout handling to make it more robust

## [2.3.2] - 2024-02-21

- Add `max_connection` parameter in resource clients to allow for more control over the number of network connections

## [2.3.1] - 2024-01-16

- fix auth resolution logic

## [2.3.0] - 2024-01-15

- allow to reuse existing auth session

## [2.0.0] - 2023-11-17

- Drop support for pydantic v1.X.Y

## [1.4.3] - 2023-11-07

- Add default values for `PaginatedResponse` fields after pydantic update

## [1.4.2] - 2023-11-03

- Add support for pydantic > 2.0.0

## [1.4.1] - 2023-10-19

- Expose AsyncFileResourceClient from cloud_storage package

## [1.4.0] - 2023-10-02

- Added delete method to `HttpClient`

## [1.3.0] - 2023-09-27

- Support for asynchronous callbacks in `UploadSpec`

## [1.2.0] - 2023-05-30

- Async support for file resource client. The synchronous client is now using async handlers behind the scenes.

## [1.1.0] - 2023-05-10

- Failed requests will be retried in a wider range of cases than previously, including both API calls and cloud storage.

## [1.0.3] - 2022-12-02

- Improve handling of network errors during file uploads. TCP and SSL timeout errors will now result in retries.

## [1.0.2] - 2022-11-01
- Internal re-work of scene upload handling to allow uploaded bytes from other sources than files
- Removed an unused argument from some internal methods.

## [1.0.1] - 2022-11-01
- Added string type as an option for cursor id 

## [1.0.0] - 2022-10-18
- Annotell becomes Kognic

## [0.1.1] - 2022-08-16
- Corrected user agent
- Bugfix for timeout

## [0.1.0] - 2022-05-12
- Update `annotell-auth` to 2.0.1
- Support for pagination on API requests

## [0.0.1] - 2022-04-01

- Library created
