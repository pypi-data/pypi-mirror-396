# راهنمای توسعه

این راهنما نحوه توسعه و مشارکت در فریمورک WeWork را توضیح می‌دهد.

## Setup Development Environment

```bash
# کلون کردن
git clone https://github.com/wecanco/WeWork.git
cd wework-framework

# نصب در حالت development
pip install -e .
```

## Code Style

### Python

- PEP 8
- Type hints
- Docstrings

### JavaScript

- ESLint
- Prettier
- JSDoc

## Testing

```bash
pytest tests/ -v
```

## مراحل بعدی

- [تست‌نویسی](./testing.md)
- [بهینه‌سازی](./performance.md)

