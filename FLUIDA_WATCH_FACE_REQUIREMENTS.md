# FLUIDA: Product Requirements Document & Technical Engineering Specification
## Version 7.0 — Production-Locked Connect IQ Engineering Contract

---

## 1. Executive Summary & Toolchain Scope

**FLUIDA** is an haute-horlogerie, fluid-mechanic watch face engineered exclusively for round Garmin smartwatches compiled with the **Connect IQ SDK 9.2.0** (`connectiq-sdk-mac-9.2.0-2026-06-09-92a1605b2`) toolchain:
- **Minimum SDK Version**: `minApiLevel="4.2.0"` (SDK 9.2.0 manifest version 3 attribute; same device-API floor previously written as `minSdkVersion`). Ensures full access to `Toybox.Complications`, `SensorHistory`, and modern graphics while compiling under SDK 9.2.0 for all listed targets.
- **Compiler Directives**: `(:typecheck(strict))` enabled across all Monkey C modules.
- **Application ID**: `c4f828a1-5998-4920-bb37-9a2f778a4e91` (Standard hyphenated 8-4-4-4-12 UUID).

### Core Horological Subsystems:
1. **Left Capillary Vessel (Hours)**: Vertical column rising along a $1 \dots 12$ stepped regulator scale with dual-state AM/PM badge and 24-hour mode support.
2. **Right Capillary Vessel (Minutes)**: Vertical column rising continuously along a $00 \dots 60$ scale.
3. **Central Hydrodynamic Spirit Level (Seconds & Inclinometer)**: A calibrated fluid well featuring concentric reticles, dynamic gravity/tilt responsiveness, and dead-center digital seconds.
4. **Hourly Stepping & Siphon Flush Hydrodynamics**:
   - Hourly Rollover ($XX:59:59 \to XX:00:00$, hours $1 \to 2, \dots, 11 \to 12$): The minute vessel flushes from $60 \to 00$, and the hour column steps up by 1 hour mark.
   - 12-Hour Rollover ($12:59:59 \to 01:00:00$): **Dual Siphon Flush** — the minute vessel drains from $60 \to 00$ AND the hour vessel drains the full height from $12 \to 1$ in complete 3-stage lockstep.
5. **Modern Connect IQ Complications Engine**: Native integration with `Toybox.Complications` supporting press-and-hold (`WatchFaceDelegate.onPress`) shortcuts to launch native apps on touchscreen devices.
6. **Display-Specific Low-Power Architecture**:
   - **AMOLED**: Ultra-low-power sparse wireframe layout ($< 3.5\%$ pixel luminance) with a 16-step wandering pixel shift algorithm ($|\Delta y| \ge 3\text{ px}$ per minute).
   - **MIP**: Static dial retention with 1Hz `onPartialUpdate()` clip and `onPowerBudgetExceeded()` watchdog protection.

---

## 2. Canonical Dial Coordinate Geometry & Hardware Clearance

### 2.1 Full-Screen Watch Face Space
In Connect IQ, **the entire physical screen is the watch face dial**. 
All geometry is defined in **Normalized Unit Coordinates** $(u, v) \in [0.0, 1.0]$, where $(0.500, 0.500)$ is the exact center of the round display and $R = 0.500$ is the screen radius. On any target device with diameter $D$ (`dc.getWidth()`):
$$X = u \cdot D, \quad Y = v \cdot D, \quad \text{Radius} = r \cdot D$$

```
V = 0.00 ──────────────────────── Top Screen Rim ────────────────────────
V = 0.08                     F  L  U  I  D  A (Brand)
V = 0.14 [Top Cap 0.14..0.18]                           [Top Cap 0.14..0.18]
V = 0.22 ─── 12 ─── (Span Top)                    ─── 60 ─── (Span Top)
V = 0.23             ╭───────────────╮
                     │   (50, 33)    │  Central Spirit Level
                     │  [ 35 ] Sec   │  (Diameter = 0.20 D)
V = 0.43             ╰───────────────╯
V = 0.465                    [ AM ]     (Dual-State Badge)
V = 0.520                  O C T   14   (Single-Line Date)
V = 0.605             ♥ 72         [82%] (HR / Battery)
V = 0.665             ▲ 540        ☼ 21° (Calories / Temp)
V = 0.720 ───  1 ─── (Span Bot)                    ─── 00 ─── (Span Bot)
V = 0.760 [Manifold Ear 0.76..0.80]               [Manifold Ear 0.76..0.80]
V = 0.865                  !! 12,450 (Steps Counter)
V = 1.00 ────────────────────── Bottom Screen Rim ──────────────────────
```

### 2.2 Reconciled Coordinates & Clearance Verification
To eliminate visual collision, dimensions are mathematically locked as follows:

#### Horizontal Spacing ($D = 1.000$):
- **Left Tube (Hours)**: Center $U_{\text{left}} = 0.260$, Width $W = 0.100 \implies$ Occupies $U \in [0.210, 0.310]$.
  - Scale numerals (`1..12`) sit on the left outer flank: $U \in [0.130, 0.195]$.
- **Right Tube (Minutes)**: Center $U_{\text{right}} = 0.740$, Width $W = 0.100 \implies$ Occupies $U \in [0.690, 0.790]$.
  - Scale numerals (`00..60`) sit on the right outer flank: $U \in [0.805, 0.870]$.
- **Central Atrium**: Clear span between tube inner edges $U \in [0.310, 0.690]$ (Total Width = **$0.380 D$**, or $172.5\text{ px}$ on 454).
- **Central Spirit Level Well**: Center $(0.500, 0.330)$, Outer Radius $R_{\text{well}} = 0.100$ (Outer Diameter = **$0.200 D$**, or $90.8\text{ px}$ on 454).
  - Well spans $U \in [0.400, 0.600]$.
  - **Well-to-Tube Clearance**: $0.400 - 0.310 = \mathbf{0.090 D}$ (**$40.9\text{ px}$ on 454**, **$21.6\text{ px}$ on 240**).
- **Flank Metric Blocks**:
  - Left Metrics (HR / Calories): Center $U = 0.410$, Width $0.120 \implies U \in [0.350, 0.470]$.
    - Clearance to left tube: $0.350 - 0.310 = \mathbf{0.040 D}$ (**$18.2\text{ px}$** on 454).
  - Right Metrics (Battery / Temp): Center $U = 0.590$, Width $0.120 \implies U \in [0.530, 0.650]$.
    - Clearance to right tube: $0.690 - 0.650 = \mathbf{0.040 D}$ (**$18.2\text{ px}$** on 454).
  - Inter-column gap: $0.530 - 0.470 = \mathbf{0.060 D}$ (**$27.2\text{ px}$** on 454).

#### Vertical Spacing ($D = 1.000$):
- **Top Titanium Caps**: $V \in [0.140, 0.180]$.
- **Top Scale Marks (`12` & `60`)**: $V_{\text{top}} = 0.220$.
  - **Cap-to-Scale Clearance**: $0.220 - 0.180 = \mathbf{0.040 D}$ (**$18.2\text{ px}$** on 454, **$9.6\text{ px}$** on 240).
- **Bottom Scale Marks (`1` & `00`)**: $V_{\text{bot}} = 0.720$.
- **Manifold Mounting Ears**: $V \in [0.760, 0.800]$.
  - **Scale-to-Ear Clearance**: $0.760 - 0.720 = \mathbf{0.040 D}$ (**$18.2\text{ px}$** on 454, **$9.6\text{ px}$** on 240).
- **Spirit Well Vertical Span**: $V \in [0.330 - 0.100, 0.330 + 0.100] = [0.230, 0.430]$.
  - **Cap-to-Well Clearance**: $0.230 - 0.180 = \mathbf{0.050 D}$ (**$22.7\text{ px}$** on 454).
- **AM/PM Indicator Badge**: Positioned at $(0.500, 0.465)$ (**$0.035 D = 15.9\text{ px}$** below well rim).
- **Date Display (Single Line)**: Center $(0.500, 0.520)$. Formatted as `"OCT 14"` (or localized `"14 OCT"`).
  - Badge center is $0.465$ and date center is $0.520$ ($\Delta v = 0.055$, $13.2\text{ px}$ on 240). Cap height of both glyphs is $\le 0.028 D$ ($6.7\text{ px}$ on 240, $12.7\text{ px}$ on 454) so the two lines do not meet.
- **Flank Row 1 (HR & Battery)**: $V = 0.605$.
- **Flank Row 2 (Calories & Temp)**: $V = 0.665$.
- **Steps Counter**: $(0.500, 0.865)$ (Below manifold ears).

---

## 3. Authoritative Ground-Truth Device Matrix

Directly aligned with Connect IQ `compiler.json` definitions. All supported round targets share a **$128\text{ KB}$ (`131,072 bytes`)** watchface memory heap:

| Product ID | Display Tech | Resolution | Memory Heap | Pixel Format / Palette | Resource Directory |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `fenix7s`, `fenix7spro` | MIP Transflective | $240 \times 240$ | $128\text{ KB}$ | 8-bit `ARGB2222` (64 colors) | `resources-round-240x240` |
| `fenix7`, `fenix7pro`, `fr255`, `fr955`, `fenix8solar47mm` | MIP Transflective | $260 \times 260$ | $128\text{ KB}$ | 8-bit `ARGB2222` (64 colors) | `resources-round-260x260` |
| `fenix7x`, `fenix7xpro`, `enduro3`, `enduro4`, `fenix8solar51mm` | MIP Transflective | $280 \times 280$ | $128\text{ KB}$ | 8-bit `ARGB2222` (64 colors) | `resources-round-280x280` |
| `venu2s`, `fr265s` | AMOLED | $360 \times 360$ | $128\text{ KB}$ | 16-bit RGB 5-6-5 (65,536 colors)| `resources-round-360x360` |
| `venu3s`, `epix2pro42mm` | AMOLED | $390 \times 390$ | $128\text{ KB}$ | 16-bit RGB 5-6-5 (65,536 colors)| `resources-round-390x390` |
| `venu2`, `fr265`, `epix2`, `epix2pro47mm`, `fenix843mm` | AMOLED | $416 \times 416$ | $128\text{ KB}$ | 16-bit RGB 5-6-5 (65,536 colors)| `resources-round-416x416` |
| `fr965`, `venu3`, `epix2pro51mm`, `fenix847mm`, `fenix8pro47mm` | AMOLED | $454 \times 454$ | $128\text{ KB}$ | 16-bit RGB 5-6-5 (65,536 colors)| `resources-round-454x454` |

---

## 4. Mathematical Time, Stepping & Siphon Engine

### 4.1 Stepped Regulator Hours Model ($h \in [0, 23]$)
1. **Hour Normalization ($h_{\text{disp}} \in [1, 12]$)**:
   $$h_{\text{disp}} = (h \pmod{12} == 0) \ ?\  12 : (h \pmod{12})$$
2. **Hours Vessel Fill Fraction ($F_{\text{hour}} \in [0.0, 1.0]$)**:
   $$F_{\text{hour}} = \frac{h_{\text{disp}} - 1}{11.0}$$
   - Hour 1 ($01:00\text{–}01:59$): $F_{\text{hour}} = \frac{0}{11} = 0.0000$ (Meniscus sits on `1` tick mark).
   - Hour 10 ($10:00\text{–}10:59$): $F_{\text{hour}} = \frac{9}{11} \approx 0.8182$ (Meniscus sits on `10` tick mark).
   - Hour 12 ($12:00\text{–}12:59$): $F_{\text{hour}} = \frac{11}{11} = 1.0000$ (Meniscus sits on `12` apex tick mark).
   - Meniscus never exceeds $1.0000$ during the 12 o'clock hour.

3. **AM/PM & 24-Hour Mode**:
   - **12-Hour Mode (`!is24Hour`)**:
     A dual-state text badge is rendered at $(0.500, 0.465)$:
     - $\text{AM}$ ($0 \le h < 12$): Displays `[ AM ]` in Crisp Ice White (`#E0F7FA`).
     - $\text{PM}$ ($12 \le h < 24$): Displays `[ PM ]` in Radiant Theme Cyan (`#00E6B8`).
   - **24-Hour Mode (`is24Hour`)**:
     The badge displays the 24-hour digital string (e.g. `13:35`) centered at $(0.500, 0.465)$, removing any ambiguity while the fluid capillaries maintain the physical $1 \dots 12$ regulator scale.

### 4.2 Continuous Minutes Model ($m \in [0, 59], s \in [0, 59]$)
$$F_{\text{min}} = \frac{m + \frac{s}{60.0}}{60.0} \quad \in [0.0, 1.0)$$

### 4.3 Siphon State Machine with Edge Latch
To prevent false continuous triggering, `mLastTriggeredHour` is initialized to the current hour on startup:

```monkeyc
class FluidaModel {
    private var mLastTriggeredHour as Number;

    function initialize() {
        mLastTriggeredHour = System.getClockTime().hour;
    }

    function checkSiphonEdge(clockTime as System.ClockTime, inLowPower as Boolean, enableAnim as Boolean) as Void {
        var h = clockTime.hour;
        var m = clockTime.min;
        var s = clockTime.sec;

        if (m == 0 && s == 0 && mLastTriggeredHour != h) {
            mLastTriggeredHour = h;
            if (!inLowPower && enableAnim) {
                startSiphonAnimation(h);
            }
        }
    }
}
```

#### Siphon Flush Execution Paths ($T_{\text{total}} = 1.0\text{s}$, 30Hz Timer):

The drain predicate `hourDrainsOnRollover(h_disp)` accepts the normalized display hour $h_{\text{disp}} \in [1, 12]$ (`FluidaModel.normalizeHour(h)`) and returns `true` exclusively when $h_{\text{disp}} == 1$ (01:00 and 13:00). Every other display hour steps.

**Case A: Standard Hourly Rollover ($h_{\text{disp}} \in [2, 12]$)**:
- **Minute Vessel Drains ($60 \to 00$)**:
  - Stage 1 ($t \in [0.0\text{s}, 0.4\text{s}]$, $\tau = t / 0.4$): $F_{\text{min}}(\tau) = 1.0 \cdot (1.0 - \tau^{2.2}) \to$ reaches $0.0000$ at $\tau = 1.0$.
  - Stage 2 ($t \in [0.4\text{s}, 0.7\text{s}]$, $\tau_2 = (t - 0.4)/0.3$): $F_{\text{min}}(\tau_2) = 0.06 \cdot \sin(\pi \tau_2) \cdot e^{-3.0 \tau_2}$.
  - Stage 3 ($t \in [0.7\text{s}, 1.0\text{s}]$): Settles at $0.0000$.
- **Hour Vessel Steps**: The hour vessel meniscus **does not drain**; it steps immediately to its new index level:
  $$F_{\text{hour}} = \frac{h_{\text{disp}} - 1}{11.0}$$
  *(e.g., at 10:00:00, $F_{\text{hour}} = 9/11 \approx 0.8182$, resting on mark `10`)*.

**Case B: Dual Siphon at $12 \to 1$ ($h_{\text{disp}} == 1$)**:
Both columns drain, rebound, and settle in lockstep:
- Stage 1: $F_{\text{min}}(\tau) = 1.0 \cdot (1.0 - \tau^{2.2})$ and $F_{\text{hour}}(\tau) = 1.0 \cdot (1.0 - \tau^{2.2}) \to$ both reach $0.0000$.
- Stage 2: Both rebound to $0.06 \cdot \sin(\pi \tau_2) \cdot e^{-3.0 \tau_2}$.
- Stage 3: Both settle cleanly at $0.0000$ (Hour sits on mark `1`, Minute sits on mark `00`).

---

## 5. Inverted Fluidic Tilt Physics Engine

### 5.1 Physical Buoyancy & Sign Conventions
Garmin's 3-axis accelerometer reports in **milli-g** via `Sensor.getInfo().accel`:
- $+X$: 3 o'clock (rightward).
- $+Y$: 12 o'clock (upward).
- $+Z$: Toward viewer.

In screen coordinates, $(u=0, v=0)$ is the top-left (12 o'clock is $v = 0$, 6 o'clock is $v = 1$):
- Tilting right ($a_x > 0$): Gravity pulls liquid rightward $\implies$ buoyant bubble moves **leftward** ($-X$ direction).
- Tilting top/12 o'clock down ($a_y > 0$): Gravity pulls liquid topward $\implies$ buoyant bubble moves **downward** toward 6 o'clock ($+Y$ direction, increasing $v$).

$$\Delta x_{\text{tilt}} = -k_{\text{tilt}} \cdot \left(\frac{a_x}{1000.0}\right)$$
$$\Delta y_{\text{tilt}} = +k_{\text{tilt}} \cdot \left(\frac{a_y}{1000.0}\right)$$

### 5.2 Bubble Containment Clamp (Preventing Ink Spill)
In normalized screen units ($D = 1.0$):
- Spirit Well Center: $\vec{P}_{\text{center}} = (0.500, 0.330)$
- Outer Well Radius: $R_{\text{well}} = 0.100$ ($45.4\text{ px}$ on 454)
- Inner Fluid Boundary: $R_{\text{fluid}} = 0.092$ ($41.8\text{ px}$ on 454)
- Bubble Visual Radius: $R_{\text{bubble}} = 0.012$ ($5.4\text{ px}$ on 454)
- **Maximum Bubble Center Clamp**:
  $$R_{\text{max}} = R_{\text{fluid}} - R_{\text{bubble}} = 0.092 - 0.012 = \mathbf{0.080 D} \quad (36.3\text{ px}\text{ on } 454)$$
  *(Guarantees outer bubble boundary $0.080 + 0.012 = 0.092 \le R_{\text{fluid}}$; bubble ink can never touch or cross the glass rim).*
- Base Orbital Track: $R_{\text{track}} = 0.060 D$ ($27.2\text{ px}$ on 454).

#### Seconds Angle & Compound Position:
$$\theta_{\text{sec}} = \text{radians}(s \cdot 6.0^\circ - 90.0^\circ) \quad (s \in [0, 59])$$
$$\vec{P}_{\text{orbit}} = (R_{\text{track}} \cdot \cos\theta_{\text{sec}}, \ R_{\text{track}} \cdot \sin\theta_{\text{sec}})$$
$$\Delta X = P_{\text{orbit}.x} + \Delta x_{\text{tilt}}, \quad \Delta Y = P_{\text{orbit}.y} + \Delta y_{\text{tilt}}$$
$$d = \sqrt{\Delta X^2 + \Delta Y^2}$$
$$\vec{P}_{\text{final}} = \begin{cases} (0.500 + \Delta X, \ 0.330 + \Delta Y) & \text{if } d \le R_{\text{max}} \\ \left(0.500 + R_{\text{max}} \cdot \frac{\Delta X}{d}, \ 0.330 + R_{\text{max}} \cdot \frac{\Delta Y}{d}\right) & \text{if } d > R_{\text{max}} \end{cases}$$

#### Sensitivity Profiles ($k_{\text{tilt}}$):
- `0 (Off)`: $k_{\text{tilt}} = 0.000$
- `1 (Low)`: $k_{\text{tilt}} = 0.015$
- `2 (Medium - Default)`: $k_{\text{tilt}} = 0.030$
- `3 (High)`: $k_{\text{tilt}} = 0.045$

### 5.3 Sensor Lifecycle & EMA Damping
- **App Boot Registration**: Accelerometer starts in `onLayout()` / `initialize()` so tilt is active immediately:
  ```monkeyc
  function startAccelerometer() as Void {
      var options = {
          :period => 1, // 1-second batch interval
          :accelerometer => {
              :enabled => true,
              :sampleRate => 10 // 10Hz sampling
          }
      };
      Sensor.registerSensorDataListener(method(:onSensorData), options);
  }
  ```
- **Lifecycle Management**:
  - `onExitSleep()`: Calls `startAccelerometer()`.
  - `onEnterSleep()`: Calls `Sensor.unregisterSensorDataListener()` immediately to eliminate sleep power drain.
- **Damping Filter**: On each sample in the 10Hz batch, apply 1st-order EMA filter ($\alpha = 0.25$, $\tau = 400\text{ms}$):
  $$\hat{a}_x[n] = \hat{a}_x[n-1] + 0.25 \cdot (a_x[n] - \hat{a}_x[n-1])$$
  $$\hat{a}_y[n] = \hat{a}_y[n-1] + 0.25 \cdot (a_y[n] - \hat{a}_y[n-1])$$

---

## 6. Low-Power Architecture & Anti-Burn-In Shifter

### 6.1 AMOLED Always-On Display (AOD)
- **Active Luminance**: Total on-pixels strictly $< 3.5\%$.
- **Layout Specification**:
  - Background, bezel, and complications: 100% Solid Black (`#000000`).
  - Tubes: 1px hollow wireframe outline with a 2px horizontal meniscus indicator bar.
  - Digital Time: Centered minimalist `HH:MM` outline font.
  - Seconds subdial, bubble, and micro-ticks: **Completely removed**.
- **16-Step Wandering Pixel Shifter ($|\Delta y| \ge 3\text{ px}$)**:
  Every minute in `onUpdate()`, root draw coordinates advance along this verified sequence:
  ```
  Step 0:  ( 0,  0)     Step 4:  (-3, +3)     Step 8:  (-3, +3)     Step 12: (-3, +4)
  Step 1:  (+3, +3)     Step 5:  (+4, -3)     Step 9:  (+4, -4)     Step 13: (+4, -4)
  Step 2:  (-3, -3)     Step 6:  (-4, +4)     Step 10: (-4, +3)     Step 14: (-4, +3)
  Step 3:  (+3, -6)     Step 7:  (+3, -4)     Step 11: (+3, -3)     Step 15: (+3, -4)
  Wrap Step 15 -> 0: dx = -3, dy = +4; |dy| = 4 >= 3
  ```
  Because $|\Delta y| \ge 3\text{ px}$ on every single step, a 2px meniscus bar completely clears its physical OLED footprint every minute.

### 6.2 MIP Transflective Low Power
Applies to every MIP product in section 3 (`fenix7`, `fenix7s`, `fenix7x`, `fenix7pro`, `fenix7spro`, `fenix7xpro`, `fr255`, `fr955`, `fenix8solar47mm`, `fenix8solar51mm`, `enduro3`, `enduro4`).
- MIP displays do not suffer burn-in; pixel shifting is bypassed (`requiresBurnInProtection == false`).
- Background dial and static scales remain visible in sleep.
- **1Hz Seconds via `onPartialUpdate()`**:
  - Bounded strictly to the central well clip:
    `dc.setClip((0.400 * D).toNumber(), (0.230 * D).toNumber(), (0.200 * D).toNumber(), (0.200 * D).toNumber())`.
  - Inside that clip, each frame first fills the well floor `#121820`, then draws the digital seconds and the orbital bubble. Drawing the new bubble alone leaves the previous bubble on the glass.
  - **Power Budget Watchdog**: If `onPowerBudgetExceeded()` is called by the OS, `mPowerBudgetExceeded = true` is latched; partial updates immediately cease until cleared on the next wrist wake (`onExitSleep()`). The OS limit is `WatchFacePowerInfo.executionTimeLimit`, not a fixed $2\text{ ms}$ budget.

---

## 7. Complications Engine & Telemetry Specifications

### 7.1 Subscribed Complications and Press-and-Hold Launch Targets
Five native complications are subscribed. In Connect IQ, a short tap on a running watch face does not launch complications (`onTap` only fires in watch face edit/customization mode). Interactive complication shortcuts on the running face are triggered via touch-and-hold: `WatchFaceDelegate.onPress(clickEvent)`.
`Complications.exitTo` takes a `Complications.Id`, built with `new Complications.Id(type)`. It does not take the raw `COMPLICATION_TYPE_*` integer.

| Dial Field | Subscribed Type | Display Number Drawn From | Press-and-Hold Launches |
| :--- | :--- | :--- | :--- |
| **Steps** | `COMPLICATION_TYPE_STEPS` | Complication value (if non-null), else `ActivityMonitor.getInfo().steps` | That id |
| **Heart Rate** | `COMPLICATION_TYPE_HEART_RATE` | `SensorHistory` (5-minute window, clamped to $[30, 240]$). The complication does not provide this history window; it serves as launch target only. | That id |
| **Battery** | `COMPLICATION_TYPE_BATTERY` | `System.getSystemStats()` (percentage or `batteryInDays`). The complication is percentage-only; it serves as launch target only. | That id |
| **Calories** | `COMPLICATION_TYPE_CALORIES` | Complication value (if non-null), else `ActivityMonitor.getInfo().calories` | That id |
| **Temperature** | `COMPLICATION_TYPE_CURRENT_TEMPERATURE` | `Weather.getCurrentConditions()` (Celsius, with 3-hour stale check). Complication serves as launch target only. | That id |

```monkeyc
var stepsId = new Complications.Id(Complications.COMPLICATION_TYPE_STEPS);
Complications.exitTo(stepsId);
```

#### Touchscreen Press-and-Hold Handler (`WatchFaceDelegate.onPress`)
In `WatchFaceDelegate.onPress(clickEvent as WatchUi.ClickEvent) as Boolean`, hit-test in normalized $(u, v)$ coordinates. When a complication is launched via `Complications.exitTo`, the handler **must return `true`** to signal to the OS that the touch event was handled. If no complication is matched or the device lacks touchscreen (`!isTouchScreen`), return `false`:
- Steps: $V \in [0.820, 0.900]$
- Heart rate: $U \in [0.350, 0.470]$, $V \in [0.575, 0.635]$
- Battery: $U \in [0.530, 0.650]$, $V \in [0.575, 0.635]$
- Calories: $U \in [0.350, 0.470]$, $V \in [0.635, 0.695]$
- Weather: $U \in [0.530, 0.650]$, $V \in [0.635, 0.695]$

### 7.2 Telemetry Fallback Matrix
| Metric | API Source | Fallback / Stale Handling | Display Format |
| :--- | :--- | :--- | :--- |
| **Heart Rate** | `SensorHistory.getHeartRateHistory({:period => new Time.Duration(300), :order => SensorHistory.ORDER_NEWEST_FIRST})` | If off-wrist, null, or outside $[30, 240]\text{ bpm} \to$ `"--"` | Integer (`72`) |
| **Battery Level**| `System.getSystemStats()` | `var stats = System.getSystemStats();`<br>`BatteryMode == 0` $\to$ `(Math.round(stats.battery) as Float).toNumber().format("%d") + "%"`<br>`BatteryMode == 1` $\to$ If `stats.batteryInDays != null && stats.batteryInDays > 0` show `(Math.round(stats.batteryInDays) as Float).toNumber().format("%d") + "d"`, else fallback to percentage. *(Under `(:typecheck(strict))`, `Math.round()` returns a `Numeric`, which must be cast `as Float` before `.toNumber()` and `.format("%d")`)*. | String |
| **Daily Steps** | Safe check:<br>`var comp = Complications.getComplication(new Complications.Id(COMPLICATION_TYPE_STEPS));`<br>`var steps = (comp != null && comp.value != null) ? comp.value : ActivityMonitor.getInfo().steps;` | If permission denied or `steps == null` $\to$ `"--"` | Grouped string (`12,450`) |
| **Active Calories**| Safe check:<br>`var comp = Complications.getComplication(new Complications.Id(COMPLICATION_TYPE_CALORIES));`<br>`var cal = (comp != null && comp.value != null) ? comp.value : ActivityMonitor.getInfo().calories;` | If `cal == null` $\to$ `"--"` | Integer (`540`) |
| **Weather Temp**| `Weather.getCurrentConditions().temperature` (Celsius) | If null or `(Time.now().value() - cond.observationTime.value()) > 10800` (stale $>3\text{h}$) $\to$ `"--°"` | See temperature unit row |
| **Temperature Unit**| Setting: `-1=\text{Auto}`, `0=\text{Celsius}`, $1=\text{Fahrenheit}$ | Fahrenheit only when setting is $1$, or setting is $-1$ and `temperatureUnits == System.UNIT_STATUTE`: $T_{\text{disp}} = (\text{Math.round}(T_{\text{celsius}} \cdot 1.8 + 32.0) \text{ as Float}).\text{toNumber}()$. Otherwise $T_{\text{disp}} = (\text{Math.round}(T_{\text{celsius}}) \text{ as Float}).\text{toNumber}()$. $21^\circ\text{C}$ displays `21°` in Celsius and `70°` in Fahrenheit. | `21°` or `70°` |

---

## 8. Properties & Settings Schema

### 8.1 `properties.xml`
```xml
<properties>
    <property id="HoursFluidColor" type="number">0x0055E6</property>   <!-- Sapphire Blue -->
    <property id="MinutesFluidColor" type="number">0x00E6B8</property> <!-- Emerald Cyan -->
    <property id="SecondsFluidColor" type="number">0x00E6B8</property> <!-- Emerald Cyan -->
    <property id="CustomHexHours" type="string"></property>
    <property id="CustomHexMinutes" type="string"></property>
    <property id="CustomHexSeconds" type="string"></property>
    <property id="LinkColors" type="boolean">false</property>
    <property id="CuratedPalette" type="number">0</property>          <!-- 0=Oceanic, 1=Ember, 2=Neon, 3=Ice -->
    <property id="TempUnit" type="number">-1</property>               <!-- -1=Auto, 0=Celsius, 1=Fahrenheit -->
    <property id="BatteryMode" type="number">0</property>             <!-- 0=Percentage, 1=Days Remaining -->
    <property id="TiltSensitivity" type="number">2</property>         <!-- 0=Off, 1=Low, 2=Medium, 3=High -->
    <property id="EnableSiphonAnimation" type="boolean">true</property>
</properties>
```

### 8.2 Curated Colorways & Precedence Rules
| Index & Name | Hours Color | Minutes Color | Seconds / Bubble Color |
| :--- | :--- | :--- | :--- |
| **0: Dual Oceanic (Default)**| Sapphire Blue (`0x0055E6`)| Emerald Cyan (`0x00E6B8`) | Emerald Cyan (`0x00E6B8`) |
| **1: Solar Ember** | Crimson Ruby (`0xE6194B`) | Amber Gold (`0xF5B041`)   | Amber Gold (`0xF5B041`)   |
| **2: Cyberpunk Neon** | Amethyst Purple (`0x9B59B6`)| Electric Lime (`0x00FF7F`)| Electric Lime (`0x00FF7F`)|
| **3: Glacier Ice** | Deep Navy (`0x1A5276`)    | Arctic Ice (`0xE0F7FA`)   | Arctic Ice (`0xE0F7FA`)   |

#### Precedence Logic:
1. If `LinkColors == true`: `CuratedPalette` strictly assigns Hours, Minutes, and Seconds colors.
2. If `LinkColors == false`:
   - Check `CustomHexHours`, `CustomHexMinutes`, `CustomHexSeconds`. If string matches `^#?([0-9A-Fa-f]{6})$`, it overrides the dropdown.
   - Otherwise, fall back to the dropdown properties (`HoursFluidColor`, etc.).
3. Spirit well floor is locked to Dark Slate `#121820` (RGB: `18, 24, 32`). Seconds text is `#FFFFFF` with a 1px halo shadow to ensure $\ge 7:1$ contrast.

---

## 9. Manifest Specification (`manifest.xml`)

```xml
<iq:manifest xmlns:iq="http://www.garmin.com/xml/connectiq">
    <iq:application id="c4f828a1-5998-4920-bb37-9a2f778a4e91" type="watchface" name="@Strings.AppName" entry="FluidaApp" launcherIcon="@Drawables.LauncherIcon" minApiLevel="4.2.0">
        <iq:products>
            <iq:product id="enduro3"/>
            <iq:product id="enduro4"/>
            <iq:product id="epix2"/>
            <iq:product id="epix2pro42mm"/>
            <iq:product id="epix2pro47mm"/>
            <iq:product id="epix2pro51mm"/>
            <iq:product id="fenix7"/>
            <iq:product id="fenix7pro"/>
            <iq:product id="fenix7s"/>
            <iq:product id="fenix7spro"/>
            <iq:product id="fenix7x"/>
            <iq:product id="fenix7xpro"/>
            <iq:product id="fenix843mm"/>
            <iq:product id="fenix847mm"/>
            <iq:product id="fenix8solar47mm"/>
            <iq:product id="fenix8solar51mm"/>
            <iq:product id="fenix8pro47mm"/>
            <iq:product id="fr255"/>
            <iq:product id="fr265"/>
            <iq:product id="fr265s"/>
            <iq:product id="fr955"/>
            <iq:product id="fr965"/>
            <iq:product id="venu2"/>
            <iq:product id="venu2s"/>
            <iq:product id="venu3"/>
            <iq:product id="venu3s"/>
        </iq:products>
        <iq:permissions>
            <!-- Sensor is illegal on type="watchface" unless Background is also set.
                 The face still calls Sensor.registerSensorDataListener without that permission. -->
            <iq:uses-permission id="SensorHistory"/>
            <iq:uses-permission id="ComplicationSubscriber"/>
        </iq:permissions>
    </iq:application>
</iq:manifest>
```

---

## 10. Automated Monkey C Unit Test Suite

```monkeyc
using Toybox.Test;
using Toybox.Lang;
using Toybox.Math;

(:test)
function testHourNormalization(logger as Test.Logger) as Boolean {
    Test.assertEqual(FluidaModel.normalizeHour(0), 12);
    Test.assertEqual(FluidaModel.normalizeHour(12), 12);
    Test.assertEqual(FluidaModel.normalizeHour(13), 1);
    Test.assertEqual(FluidaModel.normalizeHour(23), 11);
    return true;
}

(:test)
function testHourFillBounded(logger as Test.Logger) as Boolean {
    for (var h = 0; h < 24; h++) {
        var f = FluidaModel.calculateHourFill(h);
        Test.assertMessage(f >= 0.0f && f <= 1.0f, "Hour fill out of bounds for hour " + h);
    }
    return true;
}

(:test)
function testSiphonDrainCompletesAtTau1(logger as Test.Logger) as Boolean {
    var f0 = FluidaPhysics.calculateDrainProgress(1.0f, 0.0f); // tau = 0.0
    Test.assertEqual(f0, 1.0f);
    var f1 = FluidaPhysics.calculateDrainProgress(1.0f, 1.0f); // tau = 1.0 (end of stage 1)
    Test.assertEqual(f1, 0.0f);
    return true;
}

(:test)
function testHourStepVersusDualDrain(logger as Test.Logger) as Boolean {
    // Case A: 10:00 rests on mark 10. The hour tube is not emptied.
    var f10 = FluidaModel.calculateHourFill(10);
    var d10 = f10 - (9.0f / 11.0f);
    if (d10 < 0.0f) {
        d10 = -d10;
    }
    Test.assertMessage(d10 < 0.0001f, "10:00 hour fill must be 9/11");
    // hourDrainsOnRollover expects h_disp in 1..12. Hour 10 normalizes to 10.
    var hDisp10 = FluidaModel.normalizeHour(10);
    Test.assertEqual(hDisp10, 10);
    Test.assertMessage(!FluidaPhysics.hourDrainsOnRollover(hDisp10), "hour 10 steps; it does not drain");

    // Noon and midnight step onto mark 12.
    Test.assertEqual(FluidaModel.calculateHourFill(0), 1.0f);
    Test.assertEqual(FluidaModel.calculateHourFill(12), 1.0f);

    // Case B settled level: 01:00 and 13:00 sit on mark 1, and only h_disp == 1 drains.
    Test.assertEqual(FluidaModel.calculateHourFill(1), 0.0f);
    Test.assertEqual(FluidaModel.calculateHourFill(13), 0.0f);

    // Drain predicate takes h_disp in 1..12; 01:00 and 13:00 both map to h_disp 1.
    var hDisp1 = FluidaModel.normalizeHour(1);
    var hDisp13 = FluidaModel.normalizeHour(13);
    Test.assertEqual(hDisp1, 1);
    Test.assertEqual(hDisp13, 1);
    Test.assertMessage(FluidaPhysics.hourDrainsOnRollover(hDisp1), "01:00 (h_disp 1) dual-drains the hour tube");
    Test.assertMessage(FluidaPhysics.hourDrainsOnRollover(hDisp13), "13:00 (h_disp 1) dual-drains the hour tube");
    return true;
}

(:test)
function testTiltInversionAndCompoundClamp(logger as Test.Logger) as Boolean {
    // 1. Tilt right (+500mg) must move bubble left (dx < 0)
    var dx = FluidaPhysics.calculateTiltDx(500, 0.030f);
    Test.assertMessage(dx < 0.0f, "Bubble must move left when tilted right");
    
    // 2. Tilt top down (+500mg) must move bubble toward 6 o'clock (dy > 0, increasing v)
    var dy = FluidaPhysics.calculateTiltDy(500, 0.030f);
    Test.assertMessage(dy > 0.0f, "Bubble must move down toward 6 o'clock when 12 o'clock tilted down");
    
    // 3. Compound clamp: Orbit (0.060) + extreme tilt (0.045) must be clamped inside R_max (0.080)
    var compoundOffset = FluidaPhysics.calculateCompoundOffset(0.060f, 0.0f, 0.045f, 0.0f, 0.080f);
    var dist = Math.sqrt(compoundOffset[0] * compoundOffset[0] + compoundOffset[1] * compoundOffset[1]);
    Test.assertMessage(dist <= 0.0801f, "Compound bubble offset must not exceed R_max");
    return true;
}
```
