# Project Completion Checklist

## Public repository — included

- [x] Algorithm-retirement policy JSON
- [x] Default-deny policy engine
- [x] Automated policy test runner
- [x] Recorded policy test report (3/3 PASS)
- [x] Guarded OpenSSL signing wrapper
- [x] Git security preflight script
- [x] Public repository documentation and scope limitations
- [x] Git ignore rules for local keys and generated artifacts

## Local lab evidence — reported, not published

- [x] ML-DSA PKI hierarchy and certificate-chain validation
- [x] TLS 1.3 mTLS
- [x] Missing/untrusted client rejection
- [x] CRL revocation validation (offline check)
- [x] SLH-DSA replacement PKI
- [x] SLH-DSA mTLS
- [x] Local guarded signing and signature verification
- [x] Tamper detection
- [x] Local execution audit

These items describe recorded local lab work. Their complete scripts, certificates, keys, and supporting files are not included in the public repository.

## Remaining for future development

- [ ] Publish safe setup instructions for reproducing the local PKI lab
- [ ] Enterprise-wide asset inventory
- [ ] Multi-service policy distribution
- [ ] HSM/KMS integration
- [ ] External interoperability testing
- [ ] Production migration and rollback testing
