# Cross-Platform Digital Identity Verifier

A full-stack web application for creating **cryptographic identity anchors** and verifying ownership of accounts across multiple platforms using **OAuth and digital signatures**.  
The system also evaluates **cross-platform identity consistency using NLP similarity algorithms**.

---

## Live Demo

**[https://identity-verifier-tt63.onrender.com/]**

---

## Features

### Authentication
- JWT authentication with 24-hour expiry  

### Identity Anchors
- Private keys encrypted using Fernet
- QR code generation for public key sharing

### Platform Verification
- OAuth 2.0 integration with GitHub and Google
- Cryptographic signatures for verification claims

### Consistency Analysis
- Username similarity using Levenshtein distance
- Display name similarity scoring
- Bio similarity using TF-IDF cosine similarity
- Weighted cross-platform consistency scoring

### Reputation System
- Positive and negative reputation events
- Trust score updates based on events

---
## License

MIT
