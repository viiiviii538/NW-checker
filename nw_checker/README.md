# nw_checker

Python + Flutter based network vulnerability scanning tool.

## Setup

### 1. Install dependencies

```bash
# Run setup script
./setup.sh

Python dependencies are listed in requirements.txt
Flutter dependencies are listed in pubspec.yaml

pytest

flutter test

src/        # Python backend modules (network scanning, vulnerability checks)
tests/      # Python tests
lib/        # Flutter frontend code

Python: 3.11.x
Flutter: 3.19.x
Platform: Windows / macOS / Linux

python src/port_scan.py

flutter run -d windows

Make sure to have pytest installed (pip install pytest) if not already in requirements.txt.

Before running flutter commands, ensure the Flutter SDK path is set correctly in your environment.

For Android builds, configure local.properties in android/ with your sdk.dir path.


