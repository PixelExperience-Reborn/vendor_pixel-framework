#!/usr/bin/env python3
"""Source-only identity/provenance audit; does not execute archived README scripts."""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
A="{http://schemas.android.com/apk/res/android}"

def check(ok,label):
    if not ok:
        raise AssertionError(label)
    print("PASS legacy Pixel framework inventory:",label)

try:
    config=(ROOT/"config.mk").read_text(encoding="utf-8")
    readme=(ROOT/"README.md").read_text(encoding="utf-8")
    sp=(ROOT/"SettingsGoogle/Android.bp").read_text(encoding="utf-8")
    ui=(ROOT/"SystemUIGoogle/Android.bp").read_text(encoding="utf-8")
    aidl=(ROOT/"interfaces/google_battery/Android.bp").read_text(encoding="utf-8")
    settings=ET.parse(ROOT/"SettingsGoogle/AndroidManifest.xml").getroot()
    systemui=ET.parse(ROOT/"SystemUIGoogle/AndroidManifest.xml").getroot()
    check("SystemUIGoogle" in config and "SettingsGoogle" in config,
          "product config would activate both Google privileged app replacements")
    check("apktool d" in readme and "d2j-dex2jar.sh" in readme
          and "DO NOT RUN THIS DIRECTLY" in readme,
          "archived README describes manual, explicitly unsafe APK extraction")
    for bp,name,base in ((sp,"SettingsGoogle","Settings"),(ui,"SystemUIGoogle","SystemUI")):
        check(f'name: "{name}"' in bp and f'"{base}"' in bp
              and "overrides:" in bp, f"{name} overrides AOSP {base}")
        for flag in ('certificate: "platform"', 'privileged: true',
                     'platform_apis: true', 'system_ext_specific: true'):
            check(flag in bp, f"{name}: {flag}")
    check(settings.get("package") == "com.android.settings", "same Settings APK package")
    check(systemui.get("package") == "com.android.systemui"
          and systemui.get(A+"sharedUserId") == "android.uid.systemui",
          "same systemui APK identity and shared UID")
    check('name: "SettingsGoogle-lib"' in sp
          and 'libs/SettingsGoogle-lib.jar' in sp,
          "prebuilt SettingsGoogle JAR must undergo rights/ABI review")
    check('name: "vendor.google.google_battery"' in aidl
          and 'stability: "vintf"' in aidl and 'owner: "google"' in aidl,
          "Pixel-only Google battery HAL AIDL does not establish mondrian service")
    for dep in ('"tensorflowlite_java"', '"vendor-pixelatoms-java"',
                '"columbus-lib"', '"elmyra-lib"', '"vendor.google.google_battery-V1-java"'):
        check(dep in ui, "historical SystemUI Google dependency: "+dep)
    check('"libtensorflowlite_jni"' in ui,
          "native TensorFlow library introduced into privileged SystemUI")
    print("PASS source-only inventory. AOSP17 Soong, code rights, CTS, SELinux, actual Google battery HAL and mondrian NOT VERIFIED.")
except (AssertionError,OSError,ET.ParseError) as e:
    print("FAIL:",e,file=sys.stderr)
    sys.exit(1)
