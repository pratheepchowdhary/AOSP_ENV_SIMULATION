# Simulated AOSP Build Environment

This project simulates a complete Android Open Source Project (AOSP) build environment. It mimics the directory structure, build commands (`m`, `mm`, `mmm`), and environment setup (`envsetup.sh`, `lunch`) of a real AOSP tree without the massive source code download or compilation times.

It is designed for:
- Testing IDE plugins.
- developing CI scripts.
- Simulating build flows.

## Getting Started

### 1. Initialize the Environment
Like real AOSP, source the environment setup script:
```bash
source build/envsetup.sh
```

### 2. Select a Target (Lunch)
Select a build target using the `lunch` command. You can pick from the menu or pass a target name.

**Interactive Menu:**
```bash
lunch
```
Output:
```text
You're building on Linux

Lunch menu... pick a combo:
     1. aosp_arm-eng
     2. aosp_arm64-eng
     ...
     8. my_custom_device-userdebug
```

**Direct Selection:**
```bash
lunch aosp_arm64-eng
```

## Build Commands

### `m`
Builds a specific module or the entire tree.
```bash
m liblog
```
Output:
```text
Run Soong UI...
Generating build.ninja...
Starting build with 1 modules...
[ 25% 1/4] // system/core:liblog cc_library stub
[ 50% 2/4] // system/core:liblog cc_library header
[ 75% 3/4] // system/core:liblog cc_library compile
[100% 4/4] // system/core:liblog cc_library link
#### build completed successfully (0:01) ####
```

### `m all_modules`
Builds every module defined in the tree (similar to `allmod` make target).
```bash
m all_modules
```

## Helper Commands

The environment provides standard AOSP helper commands to query module information.

### `allmod`
Lists all available modules.
```bash
allmod
```
**Example Output:**
```text
FrameworksRes
VendorApp
adbd
framework
libcutils
liblog
services
...
```

### `dirmods`
Lists all modules defined within a specific directory.
```bash
dirmods system/core
```
**Example Output:**
```text
liblog
libcutils
adbd
```

### `pathmod`
Prints the source directory path of a module.
```bash
pathmod liblog
```
**Example Output:**
```text
/Users/user/Projects/Aospsimulation/system/core
```

### `outmod`
Prints the predicted output file path of a module.
```bash
outmod liblog
```
**Example Output:**
```text
/Users/user/Projects/Aospsimulation/out/target/product/generic/system/lib64/liblog.fake
```

### `gomod`
Changes the current directory to the source location of a module.
```bash
gomod liblog
# Current directory is now system/core
```

### `refreshmod`
Refreshes the `module-info.json` database. Run this if you add new `Android.bp` files.
```bash
refreshmod
```

## Module Info
The build system generates a standard `module-info.json` file at:
`out/target/product/generic/module-info.json`

This file contains detailed metadata for use by IDEs and scripts:
```json
{
  "liblog": {
    "class": ["SHARED_LIBRARIES"],
    "path": ["system/core"],
    "tags": ["optional"],
    "installed": [".../out/.../liblog.fake"],
    "module_name": "liblog"
  }
}
```
