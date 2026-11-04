#!/usr/bin/env python3
"""Source-only inventory of old PE vendor pixel-framework. NEVER installs apps."""
from pathlib import Path
import re
import sys
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
A="{http://schemas.android.com/apk/res/android}"

def check(ok,name):
    if not ok: raise AssertionError(name)
    print("PASS archived pixel-framework:",name)

try:
    make=(ROOT/"config.mk").read_text()
    settings=(ROOT/"SettingsGoogle/Android.bp").read_text()
    systemui=(ROOT/"SystemUIGoogle/Android.bp").read_text()
    battery=(ROOT/"interfaces/google_battery/Android.bp").read_text()
    readme=(ROOT/"README.md").read_text()
    check("PRODUCT_PACKAGES" in make
          and re.search(r"\bSystemUIGoogle\b",make) is not None
          and re.search(r"\bSettingsGoogle\b",make) is not None,
          "legacy config.mk forces both privileged replacements into product")
    check('name: "SettingsGoogle"' in settings
          and re.search(r'overrides:\s*\[\s*"Settings"',settings) is not None,
          "SettingsGoogle overrides official Settings")
    check('name: "SystemUIGoogle"' in systemui
          and re.search(r'overrides:\s*\[\s*"SystemUI"',systemui) is not None,
          "SystemUIGoogle overrides official SystemUI")
    for label,source in (("SettingsGoogle",settings),("SystemUIGoogle",systemui)):
        check('certificate: "platform"' in source and "privileged: true" in source
              and "system_ext_specific: true" in source,
              label+" requires platform-signed privileged system_ext app")
    check('name: "SettingsGoogle-lib"' in settings
          and 'SettingsGoogle-lib.jar' in settings,
          "legacy SettingsGoogle uses imported Jar, not clean AOSP-only Java")
    for dep in ("tensorflowlite_java","libtensorflowlite_jni","vendor.google.google_battery-V1-java",
                "SystemUI-core","SystemUI_optimized_defaults"):
        check(dep in systemui,"legacy SystemUI graph includes "+dep)
    check('name: "vendor.google.google_battery"' in battery
          and 'stability: "vintf"' in battery and 'owner: "google"' in battery,
          "legacy Google battery AIDL is not a mondrian hardware service")
    settings_manifest=ET.parse(ROOT/"SettingsGoogle/AndroidManifest.xml").getroot()
    ui_manifest=ET.parse(ROOT/"SystemUIGoogle/AndroidManifest.xml").getroot()
    check(settings_manifest.get("package")=="com.android.settings",
          "privileged replacement Settings package identity")
    check(ui_manifest.get("package")=="com.android.systemui"
          and ui_manifest.get(A+"sharedUserId")=="android.uid.systemui",
          "privileged replacement SystemUI shared UID and identity")
    check("not a guide or automation script" in readme and "DO NOT RUN THIS DIRECTLY" in readme,
          "upstream README warns old decompiled resource recipe unsafe")
    print("PASS: source-only classification. No APKs installed, old scripts run or device APIs tested.")
except (AssertionError,OSError,ET.ParseError) as err:
    print("FAIL:",err,file=sys.stderr)
    sys.exit(1)
