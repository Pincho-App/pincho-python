# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

The Pincho team takes security bugs seriously. We appreciate your efforts to responsibly disclose your findings.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub/GitLab issues.**

Instead, please report security vulnerabilities by:

1. **Opening a security advisory** on GitHub:
   - Go to https://github.com/Pincho-App/pincho-python/security/advisories/new
   - Provide detailed information about the vulnerability

2. **Include the following information**:
   - Type of vulnerability (e.g., injection, authentication bypass, etc.)
   - Full paths of source file(s) related to the vulnerability
   - Location of affected source code (tag/branch/commit or direct URL)
   - Step-by-step instructions to reproduce the issue
   - Proof-of-concept or exploit code (if possible)
   - Impact of the vulnerability (what an attacker could do)
   - Suggested fix (if you have one)

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours
- **Updates**: We will send you regular updates about our progress (at least every 5 business days)
- **Validation**: We will work to validate the vulnerability and determine its impact
- **Fix**: We will work on a fix and prepare a security release
- **Disclosure**: We will coordinate with you on the disclosure timeline

### Disclosure Policy

- **Coordinated disclosure**: We prefer coordinated disclosure and will work with you on timing
- **Security advisories**: We will publish security advisories for confirmed vulnerabilities
- **Credit**: We will credit you in the security advisory (unless you prefer to remain anonymous)

### Security Best Practices for Users

When using the Pincho Python library:

1. **Keep dependencies updated**: Regularly update the library and its dependencies
   ```bash
   pip install --upgrade pincho
   ```

2. **Protect your credentials**: Never commit API tokens to version control
   ```python
   # Good: Use environment variables
   token = os.getenv("PINCHO_TOKEN")

   # Bad: Hardcoded credentials
   token = "abc12345"  # Don't do this!
   ```

3. **Use virtual environments**: Isolate your project dependencies
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Validate input**: If accepting user input for notifications, sanitize and validate

5. **Use HTTPS**: The library uses HTTPS by default - don't override with HTTP

6. **Monitor for updates**: Watch the repository for security advisories

### Known Security Considerations

#### API Token Security

- Pincho API tokens (8-character strings) are sensitive credentials
- Store them securely (environment variables, secret managers)
- Rotate tokens if compromised
- Use token-specific permissions when available

#### Network Security

- The library communicates over HTTPS with TLS encryption
- Ensure your environment doesn't disable certificate verification
- Be cautious when using custom `base_url` parameter (testing only)

#### Dependency Security

The library has minimal dependencies:
- `httpx >= 0.24.0` - Actively maintained, security-focused HTTP client

We monitor dependencies for known vulnerabilities and update promptly.

## Security Updates

Security updates will be released as:
- **Patch versions** (e.g., 1.0.1) for minor security fixes
- **Minor versions** (e.g., 1.1.0) for security fixes requiring API changes

Security releases will:
- Be clearly marked in release notes
- Include a security advisory
- Describe the vulnerability and impact
- Provide upgrade instructions

## Hall of Fame

We recognize security researchers who responsibly disclose vulnerabilities:

<!-- Security researchers will be listed here after coordinated disclosure -->

## Questions?

If you have questions about this security policy, please open a public issue or contact us at **support@pincho.app**.

---

**Last updated**: 2025-10-26
