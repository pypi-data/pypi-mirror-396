# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via one of the following methods:

### Email

Send an email to: security@meggy-ai.com (or your project security email)

Include:
- Type of vulnerability
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### GitHub Security Advisory

You can also report vulnerabilities through GitHub's private vulnerability reporting:

1. Go to the [Security tab](https://github.com/meggy-ai/bruno-memory/security)
2. Click "Report a vulnerability"
3. Fill in the details

## Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: 
  - Critical vulnerabilities: 7-14 days
  - High vulnerabilities: 14-30 days
  - Medium vulnerabilities: 30-60 days
  - Low vulnerabilities: 60-90 days

## Disclosure Policy

- We will acknowledge your report within 48 hours
- We will provide a detailed response within 7 days indicating next steps
- We will keep you informed of the progress towards a fix
- We will notify you when the vulnerability is fixed
- We may ask for additional information or guidance

## Security Update Process

1. The vulnerability is reported and confirmed
2. A fix is prepared in a private repository
3. A new version is released with the security fix
4. A security advisory is published
5. The vulnerability is disclosed after users have had time to update

## Security Best Practices

When using bruno-memory, we recommend:

### Data Protection
- **Encryption**: Use the built-in encryption features for sensitive data
  ```python
  from bruno_memory.utils.security import encrypt_at_rest
  encrypted_messages = encrypt_at_rest(messages, password="secure-password")
  ```

- **Anonymization**: Anonymize data before analysis
  ```python
  from bruno_memory.utils.security import anonymize_for_analysis
  anonymized = anonymize_for_analysis(memories, mode="pseudonymize")
  ```

### Access Control
- Implement proper authentication and authorization
- Use audit logging to track data access
  ```python
  from bruno_memory.utils.security import AuditLogger
  logger = AuditLogger()
  logger.log_access(user_id="user123", action="read", resource_type="memory")
  ```

### Environment Security
- Never commit sensitive credentials to version control
- Use environment variables for configuration
- Rotate database credentials regularly
- Use connection pooling with appropriate limits

### Database Security
- Use parameterized queries (built into all backends)
- Enable SSL/TLS for database connections
- Regularly backup your data
- Monitor for unusual access patterns

### GDPR Compliance
- Implement data export and deletion
  ```python
  from bruno_memory.utils.security import GDPRCompliance
  gdpr = GDPRCompliance(backend)
  # Export user data
  user_data = gdpr.export_user_data(messages, memories, user_id="user123")
  # Prepare for deletion
  to_delete = gdpr.prepare_deletion(user_id="user123")
  ```

## Known Security Considerations

### Vector Database Security
- ChromaDB and Qdrant backends store embeddings that may contain semantic information
- Consider the sensitivity of data being embedded
- Use encryption at rest when available

### Redis Backend
- Redis does not have built-in authentication in default configuration
- Always use password authentication in production
- Consider using Redis ACLs for fine-grained access control

### SQLite Backend
- File-based database is only as secure as filesystem permissions
- Use encryption features for sensitive deployments
- Not recommended for multi-tenant production use

### PostgreSQL Backend
- Use SSL connections in production
- Implement row-level security for multi-tenant deployments
- Regular security updates of PostgreSQL server

## Third-Party Dependencies

We regularly monitor and update our dependencies for security vulnerabilities. Key dependencies:

- **cryptography**: Used for encryption features
- **pydantic**: Used for data validation
- **SQLAlchemy**: Used for database abstraction
- **Redis/PostgreSQL drivers**: Keep updated to latest secure versions

Run `pip-audit` to check for known vulnerabilities:
```bash
pip install pip-audit
pip-audit
```

## Security Contacts

- **Security Email**: security@meggy-ai.com
- **GitHub Security**: https://github.com/meggy-ai/bruno-memory/security

Thank you for helping keep bruno-memory and its users safe!
