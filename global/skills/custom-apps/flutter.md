# Flutter / Dart mobile apps

## Architecture (official Flutter app-architecture guide)
- **MVVM in two layers.**
  - UI layer: views plus view models, one view model per view, holding UI state and commands.
  - Data layer: repositories plus services. Repositories are the source of truth for app data and do not depend on each other; services are stateless wrappers around APIs, storage and plugins.
- **Domain layer** (use-cases) only when logic is complex or shared across view models.
- **Recommended by the guide**: `provider` for dependency injection, `go_router` for navigation, `freezed` or `built_value` for immutable models. `ChangeNotifier` is fine for view models.
- **Existing apps** (for example GetX-based ones) keep their pattern. Changing state management is a design decision with an ADR, never a drive-by refactor.

## Configuration and environments
- Flavors or `--dart-define-from-file` for UAT and production (API base URL, feature flags). Vendor secrets live on the backend, never in the app; the app talks only to our API.
- Signing keys and keystores live in a secret store or CI secrets, never in git. Use Play App Signing.
- Version is `x.y.z+build`, and the build number always increases ([releases.md](../eng-ship/releases.md)).

## Store and platform rules
- **Lending, KYC and payment apps**: read the current Google Play and App Store financial-services policies before building, because loan tenure, APR disclosure and regulatory declarations decide whether the app is approved. Request only the permissions the flow needs; the RBI Directions forbid access to contacts, media and call logs (skill `fintech-lending`).
- Permissions are asked in context, with a reason screen. The app degrades gracefully when one is denied.

## Quality
- Many unit and widget tests, plus integration tests (`integration_test`) for the key journeys. Use `patrol` when native dialogs must be driven, and golden tests for important screens ([tooling.md](../eng-testing/tooling.md)).
- `flutter analyze` clean, `dart format` applied.
- Test release builds on real low-end Android devices: camera, KYC capture, payments, poor network.
- Crash and error reporting is wired in before the first store release.

Sources (checked 2026-11-04): docs.flutter.dev/app-architecture (guide and recommendations), docs.flutter.dev/testing, Flutter releases (3.47, Dart 3.13).
