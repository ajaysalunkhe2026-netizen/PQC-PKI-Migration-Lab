# PQC PKI Migration Lab — mTLS Test Report

Date: 2026-11-07

## Environment
- OpenSSL: 4.1.0
- TLS version: TLS 1.3
- Client/server authentication: Mutual TLS
- Signature algorithm: ML-DSA-65
- Hybrid key exchange: X25519MLKEM768
- Cipher suite observed: TLS_AES_256_GCM_SHA384
- Test endpoint: 127.0.0.1:8443

## Test 1 — Valid Client Certificate
Expected: Accept the client certificate.
Observed: CONNECTION ESTABLISHED; Verification: OK.
Result: PASS

## Test 2 — Missing Client Certificate
Expected: Reject the TLS handshake.
Observed: TLS alert certificate required.
Result: PASS

## Test 3 — Untrusted Client Certificate
Expected: Reject the self-signed client certificate.
Observed: TLS alert unknown ca (alert 48).
Result: PASS

## Important Verification Notes
- Server certificate verification succeeded in the client output.
- The valid client certificate was verified against the Root CA through the Intermediate CA.
- Missing and untrusted client certificate tests were rejected.
- These tests demonstrate local lab behaviour, not production readiness.

## Limitations
- No independent interoperability testing has been performed.
- No performance benchmarking has been performed.
- No revocation, CRL or OCSP testing has been performed.
- No production HSM/KMS integration has been performed.
