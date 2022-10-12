# flake8-import

## Rules

- X100: use `from ... import ...`
- X200: use `import ...`
- X300: use `import ... as ...`

## Config

TODO toml is better ?

```yaml
rules:
  - module: datetime
    import:
      enabled: true
      allowed_asnames: ["dt"]
    import_from:
      enabled: false
```
