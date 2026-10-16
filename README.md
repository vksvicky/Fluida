# Fluida

A round watch face with two fluid columns, a seconds well, and complication shortcuts.

## Build

Requires the Connect IQ SDK. The scripts follow the same shape as Lunara.

```bash
./build.sh enduro4      # compile that device and open the simulator
./build.sh --no-sim enduro4
./export_iq.sh skip     # every device, store package, current version
./export_iq.sh patch    # bump the patch number, then build bin/Fluida.iq
```

The first build creates a local `developer_key.der`. That key stays on this machine. `./export_iq.sh` writes `bin/Fluida.iq` and `bin/RELEASE_NOTES.txt`.

## Tests and reports

```bash
./run_tests.sh unit --skip-device   # Python suite → test_output/unit_report.html
./run_tests.sh ui --update-baselines
./run_tests.sh ui                   # visual gallery → test_output/visual_report.html
./profile_memory.sh                 # test_output/memory_report.html
./run_tests.sh sim fenix7
```

The visual report mocks the spec layout (well, hour column, minute column) until the watch face draws it. Details are in `test/README.md`.

Python image checks need Pillow: `pip install -r tools/requirements.txt`.
