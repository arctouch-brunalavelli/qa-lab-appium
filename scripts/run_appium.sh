#!/usr/bin/env bash
# UiAutomator2 needs ANDROID_HOME (or ANDROID_SDK_ROOT) when Appium starts.
export ANDROID_HOME="${ANDROID_HOME:-$HOME/Library/Android/sdk}"
export ANDROID_SDK_ROOT="${ANDROID_SDK_ROOT:-$ANDROID_HOME}"
export PATH="$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$ANDROID_HOME/cmdline-tools/latest/bin"

# Use Appium from nvm (user-owned global) when available, not Homebrew’s global npm path
# that can hit EACCES. See https://github.com/nvm-sh/nvm
export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
if [ -s "$NVM_DIR/nvm.sh" ]; then
  # shellcheck source=/dev/null
  . "$NVM_DIR/nvm.sh"
  nvm use default >/dev/null 2>&1 || true
fi
exec appium "$@"
