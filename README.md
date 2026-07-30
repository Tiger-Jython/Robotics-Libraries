# TigerJython Robotics Libraries

This repository contains all TigerJython robotics modules (for micro:bit and Calliope mini boards), along with a minification script. Minification keeps memory usage low on the microcontrollers themselves. The package ships both the minified and the original, human-readable source for every library, plus a small typed JS/TS API, so it can be dropped into other applications without vendoring the repo as a git submodule.

## Install

From the npm registry:

```bash
npm install @tigerpython/robotics-libraries
```

Directly from this git repository (e.g. to track `main` or pin a specific commit/tag/branch instead of a published version):

```bash
npm install git+https://github.com/Tiger-Jython/Robotics-Libraries.git
# or pinned to a tag/branch/commit:
npm install git+https://github.com/Tiger-Jython/Robotics-Libraries.git#v1.4.0
```

## Usage

### Typed API

```ts
import { getLibrary, getRawLibrary, listLibraries, listDevices } from "@tigerpython/robotics-libraries";

listDevices();             // ["calliope", "microbit"]
listLibraries("calliope"); // ["callibot", "callibotmot", ..., "cputils"]
getLibrary("microbit", "mbrobot");    // minified source
getRawLibrary("microbit", "mbrobot"); // original, unminified source
```

The full library maps are also exported directly if you'd rather work with the plain objects:

```ts
import {
  calliopeLibraries, calliopeRawLibraries,
  microbitLibraries, microbitRawLibraries,
} from "@tigerpython/robotics-libraries";
```

### Raw `.py` files

Every device's original `.py` sources are published as part of the package and reachable via subpath exports, so bundlers that support raw/text imports (e.g. Vite) can import them directly instead of going through the JS API:

```ts
import cpglowSource from "@tigerpython/robotics-libraries/calliope/cpglow.py?raw";
```

## Attribution

The following files are taken from the [APLU Libraries](https://github.com/Tiger-Jython/Aplu-Libraries)
- callibot.py
- callibotmot.py
- cbalarm.py
- cpglow.py
- cpmike.py
- cprover.py
- cputils.py
- mbalarm.py
- mbglow.py
- mbled
- mbrobot_plus.py
- mbrobot_plusV2
- mbrobotmot

## Development

Regenerating the minified/raw JSON bundles requires Python 3 with [`python-minifier`](https://pypi.org/project/python-minifier/) installed:

```bash
pip install python-minifier
npm run build       # regenerates calliope/ and microbit/ JSON + minified .py, then builds dist/
```

A pre-commit hook (via husky) runs the Python minification step automatically and stages the regenerated files.
