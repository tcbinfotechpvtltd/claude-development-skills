---
paths:
  - "**/pubspec.yaml"
  - "**/lib/**/*.dart"
---
# eng-os rule: Flutter app code
Applies because Flutter app code is being touched. Architecture and release procedures: skill `custom-apps` ([flutter.md](../skills/custom-apps/flutter.md)).
- No vendor keys or secrets in the app; privileged calls go through our backend.
- Tokens live in secure storage (Keychain/Keystore), never in shared preferences.
- Only the permissions the flow needs; lending apps never read contacts, media or call logs.
- The app's existing state-management pattern is kept; changing it needs an ADR.
