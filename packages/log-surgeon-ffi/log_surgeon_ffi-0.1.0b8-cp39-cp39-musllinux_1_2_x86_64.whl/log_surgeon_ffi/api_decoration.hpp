#ifndef LOG_SURGEON_FFI_API_DECORATION_HPP
#define LOG_SURGEON_FFI_API_DECORATION_HPP

/**
 * `LOG_SURGEON_FFI_METHOD` should be added at the beginning of a function's
 * declaration/implementation to decorate any APIs that are directly invoked by
 * Python's interpreter. The macro expands to `extern "C"` to ensure C linkage.
 */
#define LOG_SURGEON_FFI_METHOD extern "C"

#endif  // LOG_SURGEON_FFI_API_DECORATION_HPP
