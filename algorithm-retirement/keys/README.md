# Local Lab Keys

Place the local SLH-DSA signing key pair in this directory:

- `slh-dsa-private.pem`
- `slh-dsa-public.pem`

These files are required by `../guarded_sign.py` for the local signing demonstration. Generate or provision them using your local OpenSSL setup. **Do not commit private keys or other secret material to the public repository.** Key files are ignored by the repository's `.gitignore` rules.
