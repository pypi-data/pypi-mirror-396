# CI/CD

این سند نحوه استفاده از CI/CD در فریمورک WeWork را توضیح می‌دهد.

## GitHub Actions

```yaml
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pytest
```

## مراحل بعدی

- [راهنمای استقرار](./deployment.md)
- [Docker](./docker.md)

