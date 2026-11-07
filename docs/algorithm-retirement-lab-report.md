# PQC PKI Migration and Algorithm Retirement Lab

## 1. Project Objective

Demonstrate a laboratory architecture for post-quantum PKI migration, cryptographic algorithm retirement, replacement trust chains, and policy-controlled cryptographic operations.

The central design principle is that an algorithm should have a planned retirement and replacement path before deployment.

## 2. Environment

- Operating system: Windows
- OpenSSL: 4.1.0
- Python: 3.15.1
- TLS version tested: TLS 1.3
- Environment classification: LAB

## 3. Implemented Components

### ML-DSA PKI
- ML-DSA-65 Root CA
- ML-DSA-65 Intermediate CA
- Client and server certificates
- Certificate-chain verification

### TLS and mTLS
- TLS 1.3 handshake
- X25519MLKEM768 key exchange group
- ML-DSA-65 certificate authentication
- Missing client certificate rejection
- Untrusted client certificate rejection

### Certificate Revocation
- Dedicated OpenSSL CA database
- Certificate revocation with keyCompromise reason
- CRL generation
- CRL signature verification
- Offline certificate revocation enforcement

### SLH-DSA Replacement PKI
- SLH-DSA-SHA2-128s Root CA
- SLH-DSA-SHA2-128s Intermediate CA
- Client and server certificates
- Certificate-chain verification
- SLH-DSA mTLS test

### Algorithm Retirement
- JSON-based algorithm policy
- Default-deny policy evaluation
- Automated policy test runner
- OpenSSL execution guard
- SLH-DSA signing and signature verification
- Tampered-message rejection
- JSONL execution audit log

## 4. Algorithm Retirement Policy

| Algorithm | Policy | Behaviour |
|---|---|---|
| ML-DSA-65 | DENY | OpenSSL execution blocked |
| SLH-DSA-SHA2-128s | ALLOW | Signing and verification successful |
| ML-DSA-44 | DENY | Unapproved algorithm rejected |

The policy engine uses an explicit approved list and denies algorithms that are retired or not approved.

## 5. Test Results

| Test | Result |
|---|---|
| ML-DSA-65 signature generation and verification | PASS |
| Modified ML-DSA message rejection | PASS |
| ML-DSA root certificate verification | PASS |
| ML-DSA intermediate certificate verification | PASS |
| ML-DSA client/server certificate-chain verification | PASS |
| TLS 1.3 with X25519MLKEM768 | PASS |
| Valid ML-DSA mTLS client authentication | PASS |
| Missing client certificate rejection | PASS |
| Untrusted client certificate rejection | PASS |
| CRL generation and signature verification | PASS |
| Revoked certificate rejected by offline CRL check | PASS |
| SLH-DSA replacement trust-chain verification | PASS |
| SLH-DSA mTLS test | PASS |
| Automated retirement policy tests | 3/3 PASS |
| Retired ML-DSA-65 execution blocked | PASS |
| Approved SLH-DSA signing | PASS |
| Approved SLH-DSA signature verification | PASS |
| Tampered SLH-DSA message rejected | PASS |

## 6. Evidence Locations

- algorithm-retirement/policies/algorithm-policy.json
- algorithm-retirement/policy_engine.py
- algorithm-retirement/run_tests.py
- algorithm-retirement/guarded_sign.py
- algorithm-retirement/results/retirement-policy-test-report.json
- algorithm-retirement/results/execution-audit.jsonl
- algorithm-retirement/results/sample-message.txt
- algorithm-retirement/results/guarded-signature.bin
- algorithm-retirement/results/tampered-message.txt
- algorithm-retirement/keys/

Additional PKI, CRL, and mTLS evidence is stored under:
- classical-pki/
- pqc-pki/
- clients/
- tests/
- results/

## 7. Architecture and Security Observations

1. Algorithm retirement must be distinct from certificate revocation.
2. A replacement algorithm requires new keys and replacement certificates; an existing private key cannot be converted into a different algorithm's private key.
3. Trust-chain migration involves more than changing an algorithm name.
4. Policy enforcement must occur before cryptographic operations.
5. A default-deny policy prevents unapproved algorithms from being used through the guarded application path.
6. Audit records should capture policy decisions and execution outcomes.
7. Algorithm families have different cryptographic properties and operational dependencies; replacement decisions require security and interoperability review.

## 8. Limitations

- This is a laboratory implementation, not a production enterprise deployment.
- The Python execution guard controls only operations routed through that wrapper. It does not globally disable algorithms in OpenSSL or other applications.
- The retirement policy is a manually maintained JSON policy, not a distributed enterprise policy service.
- The CRL test demonstrates offline revocation checking; it does not demonstrate automatic CRL checking by every TLS server.
- No independent multi-vendor interoperability assessment has been completed.
- No production HSM, cloud KMS, hardware firmware, or external partner migration has been tested.
- No enterprise-wide cryptographic asset inventory or automated dependency discovery has been implemented.
- No production performance, scale, disaster recovery, or rollback testing has been completed.

## 9. Future Work

- Cryptographic asset inventory and dependency mapping
- Policy distribution and enforcement across multiple services
- Certificate and key lifecycle migration automation
- HSM and cloud KMS integration
- Multi-vendor interoperability testing
- Rollback, recovery, and trust-continuity testing
- Algorithm-specific retirement runbooks
- Production-grade audit integrity and access controls

## 10. Conclusion

The lab demonstrates a controlled PQC PKI environment with ML-DSA authentication, SLH-DSA replacement trust infrastructure, TLS 1.3 mTLS, certificate revocation checks, and policy-controlled signing.

Most importantly, it demonstrates that a retired algorithm can be blocked before a guarded cryptographic operation while an approved replacement can perform real signing and verification.

This is a proof of concept for algorithm exit architecture, not a claim of complete enterprise crypto-agility or production readiness.
