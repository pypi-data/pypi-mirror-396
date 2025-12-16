# papyru

A minimal toolset to help developing RESTful services on top of django.

## Development

### Documentation

papyru's API documentation can be generated using `just docs`.

Alternatively, you can call `just open-docs` and take a cup of tea until the
docs appear in your browser.

### Tests

During development, you can simply run `just test-local`. It is highly
recommended to finally run the containerized tests with `just test` to ensure
compatiblity to the Python versions we use in our projects.
