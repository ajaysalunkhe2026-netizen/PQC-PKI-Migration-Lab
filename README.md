# PQC PKI Migration Lab

## Overview
A practical laboratory proof of concept for post-quantum PKI migration and cryptographic algorithm retirement.

## Architecture
ML-DSA-65 PKI
    |
    v
TLS 1.3 mTLS + X25519MLKEM768
    |
    v
Algorithm Retirement Policy
    |
    +---- ML-DSA-65 ----> DENY
    |
    +---- Unapproved ---> DENY
    |
    +---- SLH-DSA-128s -> ALLOW
                              |
                              v
                       OpenSSL Signing
                              |
                              v
                       Signature Verification
                              |
                              v
                         Audit Log

## Features
- ML-DSA-65 certificate authority hierarchy
- TLS 1.3 mutual authentication
- X25519MLKEM768 key exchange
- Certificate revocation and CRL validation
- SLH-DSA-SHA2-128s replacement trust chain
- Default-deny retirement policy
- Guarded OpenSSL signing and verification
- Tamper detection
- JSONL audit logging

## Test Execution
Run:
python algorithm-retirement\run_tests.py

## Detailed Report
docs/algorithm-retirement-lab-report.md

## Scope
Laboratory proof of concept only. Not production enterprise deployment.
