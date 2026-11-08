# PQC PKI Migration and Algorithm Retirement Lab

## 1. Project Objective

Demonstrate a laboratory architecture for post-quantum PKI migration, cryptographic algorithm retirement, replacement trust chains, and policy-controlled cryptographic operations.

The central design principle is that an algorithm should have a planned retirement and replacement path before deployment.

## 2. Environment

- Operating system: Windows (local lab)
- OpenSSL: 4.1.0 (local lab)
- Python: 3.15.1 (local lab)
- TLS version tested: TLS 1.3
- Environment classification: LAB

## 3. Implemented Components

The following PKI, TLS, and CRL components were exercised in the local lab. Their source files, certificates, and keys are not published in this repository.

### ML-DSA PKI — local lab only
- ML-DSA-65 Root CA
- ML-DSA-65 Intermediate CA
- Client and server certificates
- Certificate-chain verification

### TLS and mTLS — local lab only
- TLS 1.3 handshake
- X25519MLKEM768 key exchange group
- ML-DSA-65 certificate authentication
- Missing client certificate rejection
- Untrusted client certificate rejection

### Certificate Revocation — local lab only
- Dedicated OpenSSL CA database
- Certificate revocation with keyCompromise reason
- CRL generation
- CRL signature verification
- Offline certificate revocation enforcement

### SLH-DSA Replacement PKI — local lab only
- SLH-DSA-SHA2-128s Root CA
- SLH-DSA-SHA2-128s Intermediate CA
- Client and server certificates
- Certificate-chain verification
- SLH-DSA mTLS test

### Algorithm Retirement — public code plus local signing evidence
- JSON-based algorithm policy and default-deny policy evaluator
- Automated policy test runner
- OpenSSL execution guard
- Local SLH-DSA signing and signature verification test
- Local tampered-message rejection test
- JSONL execution audit log

## 4. Algorithm Retirement Policy

| Algorithm | Policy | Behaviour |
|---|---|---|
| ML-DSA-65 | DENY | OpenSSL execution blocked by the wrapper policy |
| SLH-DSA-SHA2-128s | ALLOW | Approved by policy; local signing and verification reported separately |
| ML-DSA-44 | DENY | Unapproved algorithm rejected |

The policy engine uses an explicit approved list and denies algorithms that are retired or not approved.

## 5. Test Results

### 5.1 Publicly reproducible policy tests

The public repository contains the policy engine, policy JSON, test runner, and recorded JSON output. Run `python algorithm-retirement/run_tests.py` (or the platform-equivalent path syntax) to execute the three policy tests again.

| Test | Expected | Recorded result |
|---|---|---|
| ML-DSA-65 | DENY | PASS |
| SLH-DSA-SHA2-128s | ALLOW | PASS |
| ML-DSA-44 | DENY | PASS |
| **Overall** | | **3/3 PASS** |

The committed report is a historical recorded run; a new test run writes a fresh report.

### 5.2 Lab-reported results — local evidence, not publicly reproducible from this clone

| Test | Local lab result |
|---|---|
| ML-DSA-65 signature generation and verification | PASS |
| Modified ML-DSA message rejection | PASS |
| ML-DSA root and intermediate certificate verification | PASS |
| ML-DSA client/server certificate-chain verification | PASS |
| TLS 1.3 with X25519MLKEM768 | PASS |
| Valid ML-DSA mTLS client authentication | PASS |
| Missing client certificate rejection | PASS |
| Untrusted client certificate rejection | PASS |
| CRL generation and signature verification | PASS |
| Revoked certificate rejected by offline CRL check | PASS |
| SLH-DSA replacement trust-chain verification | PASS |
| SLH-DSA mTLS test | PASS |
| Approved SLH-DSA signing and signature verification | PASS |
| Tampered SLH-DSA message rejected | PASS |

These results are reported from local lab runs. The public repository contains reports only for the PKI/mTLS/CRL work; the local scripts, certificates, keys, and full supporting evidence are not published.

## 6. Evidence Locations

### 6.1 Public evidence in this repository

- `algorithm-retirement/policy_engine.py`
- `algorithm-retirement/policies/algorithm-policy.json`
- `algorithm-retirement/run_tests.py`
- `algorithm-retirement/results/retirement-policy-test-report.json`
- `algorithm-retirement/guarded_sign.py`

### 6.2 Local lab only — not published

The following paths refer to local lab files or outputs and are not present in the public repository:

- `algorithm-retirement/keys/` — local signing keys; do not publish private material.
- `algorithm-retirement/results/sample-message.txt`
- `algorithm-retirement/results/guarded-signature.bin`
- `algorithm-retirement/results/tampered-message.txt`
- Local PKI/CA working files, certificates, and supporting scripts under `classical-pki/`, `pqc-pki/`, `clients/`, and `tests/`.
- Local CRL, mTLS, and PKI evidence referenced by the reports.

The committed `algorithm-retirement/results/execution-audit.jsonl` is a sanitized, recorded audit sample; future local audit output is ignored by Git.

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

The local lab reports a PQC PKI environment with ML-DSA authentication, SLH-DSA replacement trust infrastructure, TLS 1.3 mTLS, certificate revocation checks, and policy-controlled signing.

The publicly reproducible part of this repository is the algorithm-retirement policy engine and its three recorded policy tests. This is a proof of concept for algorithm exit architecture, not a claim of complete enterprise crypto-agility or production readiness.
