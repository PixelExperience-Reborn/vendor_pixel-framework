# P1 — PixelExperience vendor/pixel-framework Android 17 / mondrian audit

Date: 2026-11-04. Scope: **historical provenance, privilege boundaries and compatibility inventory only**. This is NOT an Android17 port and is NOT activated in the staged manifest.

**Repository audit ownership:** this is an **independent supplemental review** of the already documented P1 item, not a competing port plan. The canonical P1 matrix and [existing original audit](https://github.com/PixelExperience-Reborn/vendor_pixel-framework/blob/audit/a17-pe-native-pixel-framework-20261104/docs/ANDROID_17_PIXEL_FRAMEWORK_AUDIT.md) remain unchanged. Its [initial source CI PASS](https://github.com/PixelExperience-Reborn/vendor_pixel-framework/actions/runs/41799942680) is separately established. This supplemental review verifies binary/decompilation provenance risks, privilege declarations, and interface boundaries; no old Google components are activated.

## Historical source and original-developer approach

- PixelExperience-Reborn `vendor_pixel-framework`, archived `seventeen` HEAD `06014fc3ae69f8918ef9955b72b1484dd6948f83`. The repository contains approximately 1,807 tree entries (including 7 bundled JARs, many XML resources, Java/Kotlin classes and Pixel-specific Google AIDL).
- The README itself warns that it is a **reference workflow**, explicitly **not an automation script**. It describes decompiling vendor-customized `SystemUIGoogle.apk`/`SettingsGoogle.apk`, adjusting resource identifiers, extracting DEX into `SettingsGoogle-lib.jar` and repackaging classes/resources. This shows how previous developers approached Pixel appearance; it does **not** demonstrate permission to redistribute all components, long-term Android API compatibility, or production code quality. **Do not execute the README commands**: several explicitly warn they can break the tree.
- Historical patches include Google battery AIDL addition (`ba7ba58ff1c6de5fa97df6eda1d27c81b4abc136` historical identifier to be confirmed), Pixel specific Settings and SystemUI resources, pocket/gesture controls and an Android14 QPR1 forward-port. Not every upstream or third-party commit should be described as a PE feature.

## Verified Soong and security interfaces

`config.mk` adds both `SystemUIGoogle` and `SettingsGoogle` to `PRODUCT_PACKAGES`.

`SettingsGoogle/Android.bp`:
- `android_app { name: "SettingsGoogle", overrides: ["Settings"], certificate: "platform", privileged: true, platform_apis: true, system_ext_specific: true }`.
- `SettingsGoogle-core` links AOSP `Settings-core`, `SettingsGoogle-lib`, `google-battery`, `vendor-pixelatoms-java`, old stats/HIDL interfaces; `SettingsGoogle-lib` imports `libs/SettingsGoogle-lib.jar` as a prebuilt Java library.
- `AndroidManifest.xml` uses package `com.android.settings`, declares proprietary Google permissions/components and privileged platform permissions.

`SystemUIGoogle/Android.bp`:
- `android_app { name: "SystemUIGoogle", overrides: ["SystemUI"], certificate: "platform", privileged: true, platform_apis: true, system_ext_specific: true }`.
- `SystemUIGoogle-core` links `SystemUI-core`, `tensorflowlite_java`, `vendor-pixelatoms-java`, `columbus-lib`, `elmyra-lib`, `nga-lib`, `matchmaker-lib`, `touchcontext-lib`, `googlebattery-lib`, `vendor.google.google_battery-V1-java`, `google-battery`, and others. The app includes `libtensorflowlite_jni`. It assumes Android14-era SystemUI internal APIs, Dagger/Hilt/WM Shell resource graph and compatible Google jars.
- `AndroidManifest.xml` has package `com.android.systemui`, shared UID `android.uid.systemui`, numerous system/signature permissions and services; this is a **high-privilege platform replacement**.

`interfaces/google_battery/Android.bp` declares vendor-stable `vendor.google.google_battery` AIDL, `owner: "google"`, frozen V1, Java backend, `stability: "vintf"`. Presence of an interface is **not** evidence of a compatible HAL implementation on mondrian. Do not declare a nonexistent vendor service or relax SELinux/VINTF to satisfy these components.

## Android17 native product decision

- The reviewed staged Android17 manifest intentionally keeps **official AOSP** `frameworks/base` (SystemUI), `packages/apps/Settings`, plus AOSP modules. It does **not** include `vendor/pixel-framework`. The archived tree has no independently verified legal provenance for the bundled Google code/JARs and no demonstrated Android17 Soong compilation.
- Do **not** pull this old repository into the baseline, copy decompiled APK assets into a new project or silently install it through `config.mk`. Redistribution/license obligations, compatibility of Pixel-proprietary features, and signature/privapp security must be evaluated independently.
- The project aims for an independent PixelExperience-Reborn Android17 base. Native `device/xiaomi/mondrian` and `device/xiaomi/sm8450-common` product trees must be authored separately, not by inheriting LF52406 LineageOS-derived makefiles. Pixel proprietary services and `vendor.google.google_battery` are not equivalent to the mondrian battery HAL.
- When recreating **functionality**, use permission-cleared AOSP17 APIs and original project-owned source, individually reviewed and tested. For example, pocket mode and hardware settings belong behind actual device feature gates, not obsolete Google service classes. Optional licensed GApps packages must remain clearly separated from the core ROM.
- If a future Pixel-specific SystemUI/Settings implementation is proposed, perform an explicit rights and dependency audit first: every prebuilt JAR and resource must have known origin and redistribution authorization; all users/privileged permissions/SELinux, signatures, APK namespace and framework API changes must be verified; `m SystemUI Settings` and CTS/VTS run on both with/without GApps. Do not invent proprietary HAL implementations.

## Acceptance gates

- [x] Original developer README workflow and license/provenance risks identified.
- [x] Actual `SystemUIGoogle`/`SettingsGoogle` overriding Soong modules, privilege boundaries, prebuilt JAR and Google battery AIDL identified.
- [x] Historical source-only regression check added to audit branch (result tracked separately).
- [ ] Verify provenance and redistribution rights for all non-AOSP JARs, assets and resources. **BLOCKER**.
- [ ] Build equivalent independent AOSP17-native app components without violating Android17 package/module/resource ownership.
- [ ] Build complete AOSP17 Soong and verify actual feature/HAL/privapp/SELinux/GMS compatibility, CTS/VTS and physical mondrian boot.

**Disposition:** keep this repository as archived documentation/reference only; no automated Pixel Google app replacements, no old QPR1 sources in AOSP17 core. Source-only CI cannot prove licensing, Soong compatibility or a functional ROM.
