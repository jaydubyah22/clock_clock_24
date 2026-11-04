#!/bin/sh
set -eu
cd "$(dirname "$0")"
bundle="$PWD/build/ClockClock24.saver"
mkdir -p "$bundle/Contents/MacOS"
cp Info.plist "$bundle/Contents/Info.plist"
xcrun clang -fobjc-arc -Wall -Wextra -Werror -arch arm64 -arch x86_64 -mmacosx-version-min=11.0 -bundle -framework Cocoa -framework ScreenSaver ClockClock24View.m -o "$bundle/Contents/MacOS/ClockClock24"
codesign --force --sign - "$bundle"
printf '%s\n' "$bundle"
