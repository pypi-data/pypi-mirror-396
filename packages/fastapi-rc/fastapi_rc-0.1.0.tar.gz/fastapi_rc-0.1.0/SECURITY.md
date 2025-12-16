# Security Policy

**fastapi-rc | ©AngelaMos | 2025**

----

## Reporting a Vulnerability

We take the security of fastapi-rc seriously.

If you believe you have found a security vulnerability in this library, please report it to us as soon as possible.

### How to Report

Please open a security advisory on GitHub:

**https://github.com/CarterPerez-dev/fastapi-rc/security/advisories/new**

Or email directly:

**security@certgames.com**

### What to Include in Your Report

To help us quickly understand, reproduce, and resolve the issue, please include:

- A clear description of the vulnerability
- Steps to reproduce the issue
- Potential impact of the vulnerability
- Affected versions
- Any suggested fixes (if applicable)

### Response Timeline

- We will acknowledge receipt of your report within **48 hours**
- We will provide a detailed response within **7 days**
- We will keep you informed of our progress
- Security patches will be released as soon as possible

### Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

----

## Security Considerations

### Redis Connection Security

fastapi-rc connects to Redis using the provided URL. For production:

- **Use TLS**: `rediss://` instead of `redis://`
- **Use authentication**: Include password in URL or use Redis ACL
- **Network isolation**: Redis should not be publicly accessible
- **Connection limits**: Configure `max_connections` appropriately

Example secure connection:

```python
cachemanager.init(
    redis_url="rediss://:password@redis.internal:6379/0",
    max_connections=50,
    socket_timeout=5.0,
)
```

### Cache Poisoning

When caching user-generated content:

- Validate and sanitize data before caching
- Use separate namespaces for different trust levels
- Implement TTL limits on user-generated cache entries

### Data Sensitivity

- **Never cache sensitive data** without encryption (passwords, tokens, PII)
- Use short TTLs for sensitive cached data
- Implement proper invalidation on logout/permission changes

----

## Thank You

We appreciate your efforts to responsibly disclose your findings and will make every effort to acknowledge your contributions.
