# P1 — PixelExperience vendor/pixel-framework: Android 17 clean-base and native mondrian audit

Date: 2026-11-04. **AUDIT ONLY.** The historical project is **not enabled in staged AOSP17**. The archived PE `seventeen` branch, upstream SystemUI and Settings, and native mondrian device sources remain unchanged.

## Historical evidence

- Archive `PixelExperience-Reborn/vendor_pixel-framework`, branch `seventeen`, HEAD `06014fc3ae69f8918ef9955b72b1484dd6948f83`. Contains `SettingsGoogle`, `SystemUIGoogle`, `interfaces/google_battery`, `proto` and root `config.mk`.
- History includes port of Pixel framework features to **Android14 QPR1** (commit `d6e0c6f41715`) and Google-specific Settings/SystemUI features; it is not a port to Android17. Legacy Pixel features may be desirable, but the historical source graph is not automatically safe/compilable against current framework APIs.
- The repository's own `README.md` warns its use of APKTool/decompiled resources and scripts is a fragile *reference*, explicitly says **do not directly run** them, and calls for more careful source/resource integration. This must be treated as historical development notes, not as an approved automated source import.
- The root `config.mk` directly appends `SystemUIGoogle` and `SettingsGoogle` to `PRODUCT_PACKAGES`, with **no selection gate**. This is dangerous in a clean initial PE Android17 product.

## Build/module and privileged APK boundaries

**SettingsGoogle** `SettingsGoogle/Android.bp`:
- Has `android_app` `SettingsGoogle`, `certificate: "platform"`, `privileged: true`, `system_ext_specific: true`, `overrides: ["Settings"]`. The app uses package `com.android.settings` and imports `SettingsGoogle-lib.jar`.
- `SettingsGoogle-core` links old `Settings-core`, `android.hidl.base-V1.0-java`, `android.frameworks.stats-V1-java`, `vendor-pixelatoms-java`, `google-battery`, and inherits `Settings_manifest` and old ProGuard resources. The manifest includes privileged Google-specific intents/permissions, hardware controls and settings services.
- AOSP17 Settings has modern SPA/SettingsLib and AConfig/service contracts that must be reviewed from its **exact** Soong graph. A legacy app with the same package and broad privileges is not a resource-only overlay.

**SystemUIGoogle** `SystemUIGoogle/Android.bp`:
- Has privileged platform-signed `SystemUIGoogle` with `system_ext_specific: true`, `overrides: ["SystemUI"]`, and package `com.android.systemui`, shared UID `android.uid.systemui`.
- `SystemUIGoogle-core` extends older `SystemUI-core` and depends on `SystemUI_optimized_defaults`, Dagger, `tensorflowlite_java`, `libtensorflowlite_jni`, `googlebattery-lib`, Google `vendor.google.google_battery-V1-java`, `nga-lib`, `elmyra-lib`, `columbus-lib`, `touchcontext-lib`, `matchmaker-lib` and `vendor-pixelatoms-java`.
- Android17 SystemUI has modern Compose/flags and security-sensitive status bar, keyguard, privacy chips, Qs/notifications, media and biometric state. Do not replace the entire app to gain one Pixel feature or assume the Android14 Dagger/Service/manifest graph still resolves.
- The archive declares Google-only battery VINTF-stable AIDL `vendor.google.google_battery` (version 1; Java backend). The existence of an AIDL interface **does not imply** a matching battery service on Qualcomm Xiaomi mondrian, and must not result in fabricated VINTF HAL declarations.

## Native PE-Reborn ownership and minimum-platform policy

1. **Leave official Android17 `frameworks/base` SystemUI and `packages/apps/Settings` active** in baseline PE-Reborn. The staged manifest currently contains their official sources. Do not import this old `config.mk` or the two replacement apps as the product default.
2. PE-Reborn-specific design should be implemented as small, reviewed patches on AOSP17 or as independent resource overlays/components only when tests show stable APIs and features are appropriate for mondrian. Keep optional Pixel look-and-feel separate from boot-critical telephony, keyguard, media and recovery.
3. **No forced Google applications or licensed proprietary dependencies in AOSP-only baseline.** Verify redistributability, original source/license and module dependencies for any later optional GMS variant. Do not use the historical decompilation scripts in CI or copy signed binaries or private keys.
4. Guard features by actual hardware interfaces (UDFPS, Quick Tap, smartspace, battery charge control, proximity, now-playing, ambient, face unlock). Missing Google battery/touchcontext HALs must not be faked, and security-sensitive face unlock requires independent biometric review.
5. Independently author `device/xiaomi/mondrian` + `device/xiaomi/sm8450-common` and vendor/kernel product logic. Existing LF52406 LineageOS-derived trees are **hardware references**, never implicit PE product inheritance.
6. Verify resource precedence/duplicate resource keys, locale labels, Android17 `aapt2`, Soong source dependencies, privapp allowlists, SELinux, hidden API usage and correct packages/certificates before any optional app inclusion.
7. Validate Android17 build for both AOSP and eventual optional GMS product, UI/Settings navigation, rotation, keyguard, emergency call affordances, permissions and CTS/VTS. A source-only inventory is not such a build.

## Feature migration candidates — not approved implementations

- Visual Pixel styles and settings cards: consider standalone, minimal AOSP17 overlays if resource keys match current framework.
- Smartspace, Now Playing, screenshots/gesture and weather: optional review after core SystemUI compiles; no silent proprietary runtime requirement.
- Pixel battery/charging and reverse charging: **blocked** pending actual Xiaomi HAL hardware interface, product scope and security tests.
- Face Unlock / Pixel biometric pathways: **blocked** pending Android17 biometric security and HAL/Keyguard review.
- Anything sourced from Pixel proprietary APKs requires separate license/provenance review; the archived README is not a safe extraction recipe.

## Verification gates

- [x] Historical module build manifests, product makefile, app package identity and privileged override scope documented.
- [x] Google battery AIDL/interface and old dependencies identified.
- [x] Host-only module ownership/manifest check created; no product code imported.
- [ ] Android17 Soong/Compose/SettingsLib exact-module and dependency graph compilation.
- [ ] Functional feature-by-feature port (not global apps) against native PE-Reborn AOSP17 + mondrian trees.
- [ ] End-to-end permission, OTA, boot, CTS/VTS, userdebug/user and device regression tests.

**Decision:** mark legacy `vendor/pixel-framework` as *not suitable for baseline AOSP17 integration*. Do not import its `config.mk` or override standard Settings/SystemUI. Any future Pixel visuals must be independently designed, reviewed and tested.
