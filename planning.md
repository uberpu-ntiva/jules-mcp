
# Password Reset Feature - Implementation Plan

## Overview
Implement secure password reset functionality with email verification.

## Requirements
1. POST /api/v1/auth/password-reset - Generate reset token
2. POST /api/v1/auth/password-reset/confirm - Verify and reset
3. Token expires after 15 minutes (OWASP recommendation)
4. Rate limit: 3 requests per hour per IP
5. Email with reset link

## Architecture
- Use crypto.randomBytes(32) for token generation
- Hash tokens before storage (bcrypt)
- Store in password_reset_tokens table
- Queue email sending with retry (3 attempts)

## Security Requirements
- Generic error messages (don't reveal if user exists)
- HTTPS only
- Token single-use
- Log all reset attempts

## Testing Requirements
- Minimum 85% test coverage
- Test all edge cases (expired token, invalid token, etc.)

## Files to Create
- src/auth/PasswordResetService.ts
- src/routes/passwordReset.ts
- tests/auth/passwordReset.test.ts
- templates/password-reset-email.html

## Files to Reference
- src/auth/AuthService.ts (existing pattern)
- src/services/EmailService.ts (email sending)
- tests/auth/auth.test.ts (test pattern)
