#!/bin/sh
set -eu
cd "$(dirname "$0")"
case "${1:-}" in
    "") name=ClockClock24; dark=0; view=ClockClock24View; identifier=com.jaydubyah22.clockclock24.screensaver ;;
    --dark) name=ClockClock24Dark; dark=1; view=ClockClock24DarkView; identifier=com.jaydubyah22.clockclock24.dark.screensaver ;;
    *) printf 'Usage: %s [--dark]\n' "$0" >&2; exit 2 ;;
esac
bundle="$PWD/build/$name.saver"
mkdir -p "$bundle/Contents/MacOS"
cp Info.plist "$bundle/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier $identifier" "$bundle/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Set :CFBundleName $name" "$bundle/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Set :CFBundleExecutable $name" "$bundle/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Set :NSPrincipalClass $view" "$bundle/Contents/Info.plist"
xcrun clang -fobjc-arc -Wall -Wextra -Werror -arch arm64 -arch x86_64 -mmacosx-version-min=11.0 -DCC_DARK_MODE="$dark" -DCC_VIEW_CLASS="$view" -bundle -framework Cocoa -framework ScreenSaver ClockClock24View.m -o "$bundle/Contents/MacOS/$name"
codesign --force --sign - "$bundle"
printf '%s\n' "$bundle"
