# Changelog

## Version 0.4.0

- Update to the latest version of the **tatami** interface in the **assorthead** package.
- Support fallbacks to `tatami_python::UnknownMatrix` when a matrix class is unknown.

## Version 0.3.1

- Cast to/from `uintptr_t` so that downstream packages aren't forced to rely on **pybind11** converters.
- Added a `mattress.h` to ensure developers use the correct types during casting.
- Shift all responsibility for GC protection to C++ via the new `mattress::BoundMatrix` class.

## Version 0.3.0

- Switch to **pybind11** for the Python/C++ interface, with CMake for the build system.
- Updated to use the latest versions of the **tatami** libraries in **assorthead**.
- Renamed `tatamize()` to `initialize()` and `TatamiNumericPointer` to `InitializedMatrix`.
- Added an `initialize()` method for `SparseNdarray` objects from **delayedarray**.

## Version 0.2.0

Compatibility with NumPy 2.0

## Version 0.1 - 0.1.6

Bindings to the mattress package.
