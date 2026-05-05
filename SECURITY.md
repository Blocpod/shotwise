# Security Policy

This is a research prototype. Please report security issues privately to the project maintainers once a public repository exists.

## Scope

Relevant issues include:

- Malicious fixture files.
- Unsafe deserialization.
- Dependency confusion.
- Execution of untrusted generated scripts.

## Notes

The package does not intentionally execute fixture contents. Optional generation scripts should be inspected before use.
