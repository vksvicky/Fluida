# Fluida tests

Same report shape as the Lunara harness.

## Unit report

`./run_tests.sh unit --skip-device` runs the Python layout and export tests and writes `test_output/unit_report.html`.

`./run_tests.sh unit` then compiles Monkey C tests and runs them in the Connect IQ simulator for one device of each round size. `./run_tests.sh unit fenix7` limits the device pass to one watch.

Monkey C tests land in `test/` as the clock, siphon, and tilt logic is written. Until then, use `--skip-device`.

## Visual report

`./run_tests.sh ui` draws the spec layout at each round size, checks the well floor and the two columns, and writes `test_output/visual_report.html`.

Columns match the Lunara report:

1. Pass and assertions
2. Watch face screenshot
3. Layout zones (green columns, orange well, blue center mask)
4. Baseline, current, and diff. The center 15% is excluded. Variance above 5% fails.

```bash
./run_tests.sh ui --update-baselines
./run_tests.sh ui --device fenix7
./run_tests.sh ui --full
```

A focused run draws Dual Oceanic and Solar Ember. `--full` adds Cyberpunk Neon and Glacier Ice.

Baselines live in `test_output/baselines/`. Updating them first copies the previous set to `test_output/baselines_backup_<timestamp>/`.

## Simulator

```bash
./run_tests.sh sim fenix7
./run_tests.sh sim venu3
```

`./build.sh` and `./run_tests.sh sim` copy `bin/Fluida-settings.json` into the simulator folder Lunara uses: `$TMPDIR/com.garmin.connectiq/GARMIN/APPS/SETTINGS/FLUIDA.JSON` and `FLUIDA.SET`. That is what lets the simulator open the watch face settings.

## Memory

```bash
./profile_memory.sh
```

Writes `test_output/memory_report.html` with foreground data and code against the 128 KB watch-face limit.

## Everything

```bash
./run_tests.sh all
```

Python units, visual compare, memory profile, then simulator unit tests.
