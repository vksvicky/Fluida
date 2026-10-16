import Toybox.ActivityMonitor;
import Toybox.Application;
import Toybox.Graphics;
import Toybox.Lang;
import Toybox.Math;
import Toybox.System;
import Toybox.Time;
import Toybox.Time.Gregorian;
import Toybox.WatchUi;

(:typecheck(strict))
class FluidaView extends WatchUi.WatchFace {

    private const _MONTHS as Array<String> = [
        "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
        "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"
    ];

    private var _fontMetric as WatchUi.FontResource;
    private var _fontSteps as WatchUi.FontResource;
    private var _fontSeconds as WatchUi.FontResource;
    private var _fontDate as WatchUi.FontResource;
    private var _fontMonth as WatchUi.FontResource;
    private var _iconHeart as WatchUi.BitmapResource;
    private var _iconBattery as WatchUi.BitmapResource;
    private var _iconFlame as WatchUi.BitmapResource;
    private var _iconTemp as WatchUi.BitmapResource;
    private var _iconSteps as WatchUi.BitmapResource;
    private var _fluidHour as WatchUi.BitmapResource;
    private var _fluidMinute as WatchUi.BitmapResource;
    private var _plate as WatchUi.BitmapResource;

    function initialize() {
        WatchFace.initialize();
        _fontMetric = WatchUi.loadResource(Rez.Fonts.FaceMetric) as WatchUi.FontResource;
        _fontSteps = WatchUi.loadResource(Rez.Fonts.FaceSteps) as WatchUi.FontResource;
        _fontSeconds = WatchUi.loadResource(Rez.Fonts.FaceSeconds) as WatchUi.FontResource;
        _fontDate = WatchUi.loadResource(Rez.Fonts.FaceDate) as WatchUi.FontResource;
        _fontMonth = WatchUi.loadResource(Rez.Fonts.FaceMonth) as WatchUi.FontResource;
        _iconHeart = WatchUi.loadResource(Rez.Drawables.icon_heart) as WatchUi.BitmapResource;
        _iconBattery = WatchUi.loadResource(Rez.Drawables.icon_battery) as WatchUi.BitmapResource;
        _iconFlame = WatchUi.loadResource(Rez.Drawables.icon_flame) as WatchUi.BitmapResource;
        _iconTemp = WatchUi.loadResource(Rez.Drawables.icon_temp) as WatchUi.BitmapResource;
        _iconSteps = WatchUi.loadResource(Rez.Drawables.icon_steps) as WatchUi.BitmapResource;
        _fluidHour = WatchUi.loadResource(Rez.Drawables.fluid_hour) as WatchUi.BitmapResource;
        _fluidMinute = WatchUi.loadResource(Rez.Drawables.fluid_minute) as WatchUi.BitmapResource;
        _plate = WatchUi.loadResource(Rez.Drawables.dial_bg) as WatchUi.BitmapResource;
    }

    function onUpdate(dc as Graphics.Dc) as Void {
        var width = dc.getWidth();
        var clock = System.getClockTime();
        var secondColor = colorProperty("SecondsFluidColor", 0x00EBFF);

        dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_BLACK);
        dc.clear();
        dc.drawBitmap(0, 0, _plate);
        drawColumn(dc, width, 77, Clock.hourFill(clock.hour), _fluidHour);
        drawColumn(dc, width, 172, Clock.minuteFill(clock.min, clock.sec), _fluidMinute);
        drawSeconds(dc, width, clock.sec, secondColor);
        drawDate(dc, width);
        drawMetrics(dc, width);
    }

    private function drawColumn(dc as Graphics.Dc, width as Number, center as Number, fill as Float, sprite as WatchUi.BitmapResource) as Void {
        var colWidth = at(width, 27);
        var left = at(width, center) - colWidth / 2;
        var tubeBottom = at(width, 166);
        var spanTop = at(width, 54);
        var spanBottom = at(width, 154);
        var span = spanBottom - spanTop;
        var menY = spanBottom - (Math.round(fill * span.toFloat()) as Float).toNumber();
        var menOffset = at(width, 5);
        if (menOffset < 3) {
            menOffset = 3;
        }
        var drawTop = menY - menOffset;
        var clipHeight = tubeBottom - drawTop;
        if (clipHeight < 1) {
            return;
        }
        dc.setClip(left, drawTop, colWidth, clipHeight);
        dc.drawBitmap(left, drawTop, sprite);
        dc.clearClip();
    }

    private function drawSeconds(dc as Graphics.Dc, width as Number, second as Number, color as Number) as Void {
        var cx = at(width, 125);
        var cy = at(width, 72);
        var radius = at(width, 16);
        var radians = Math.toRadians((second * 6) - 90);
        var bx = cx + (Math.round(radius.toFloat() * Math.cos(radians)) as Float).toNumber();
        var by = cy + (Math.round(radius.toFloat() * Math.sin(radians)) as Float).toNumber();
        dc.setColor(darken(color), Graphics.COLOR_TRANSPARENT);
        dc.fillCircle(bx, by, at(width, 4));
        dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
        dc.fillCircle(bx, by, at(width, 3));
        dc.setColor(color, Graphics.COLOR_TRANSPARENT);
        dc.fillCircle(bx, by, at(width, 2));
        dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, cy, _fontSeconds, twoDigits(second), Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
    }

    private function drawDate(dc as Graphics.Dc, width as Number) as Void {
        var today = Gregorian.info(Time.now(), Time.FORMAT_SHORT);
        var month = today.month as Number;
        var day = today.day as Number;
        dc.setColor(0xA0ACB9, Graphics.COLOR_TRANSPARENT);
        dc.drawText(at(width, 125), at(width, 109), _fontMonth, spaced(_MONTHS[month - 1]), Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
        dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
        dc.drawText(at(width, 125), at(width, 120), _fontDate, day.format("%d"), Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
    }

    private function drawMetrics(dc as Graphics.Dc, width as Number) as Void {
        var stats = System.getSystemStats();
        var battery = (Math.round(stats.battery) as Float).toNumber();
        var stepsValue = ActivityMonitor.getInfo().steps;
        var stepsText = "--";
        if (stepsValue != null) {
            stepsText = grouped(stepsValue);
        }
        drawPair(dc, width, at(width, 107), at(width, 141), _iconHeart, "--", 0xF5F8FC, _fontMetric);
        drawPair(dc, width, at(width, 143), at(width, 141), _iconBattery, battery.format("%d") + "%", 0x00F07D, _fontMetric);
        drawPair(dc, width, at(width, 107), at(width, 160), _iconFlame, "--", 0xFF9128, _fontMetric);
        drawPair(dc, width, at(width, 143), at(width, 160), _iconTemp, "--", 0xFFD741, _fontMetric);
        drawPair(dc, width, at(width, 125), at(width, 201), _iconSteps, stepsText, 0x00EBFF, _fontSteps);
    }

    private function drawPair(dc as Graphics.Dc, width as Number, cx as Number, cy as Number, icon as WatchUi.BitmapResource, text as String, color as Number, font as WatchUi.FontResource) as Void {
        var gap = at(width, 3);
        var iconWidth = icon.getWidth();
        var textWidth = dc.getTextWidthInPixels(text, font);
        var start = cx - ((iconWidth + gap + textWidth) / 2);
        dc.drawBitmap(start, cy - (icon.getHeight() / 2), icon);
        dc.setColor(color, Graphics.COLOR_TRANSPARENT);
        dc.drawText(start + iconWidth + gap, cy, font, text, Graphics.TEXT_JUSTIFY_LEFT | Graphics.TEXT_JUSTIFY_VCENTER);
    }

    private function at(width as Number, basis as Number) as Number {
        return (Math.round(basis.toFloat() * width.toFloat() / 240.0f) as Float).toNumber();
    }

    private function darken(color as Number) as Number {
        var red = ((color >> 16) & 0xFF) / 5;
        var green = ((color >> 8) & 0xFF) / 5;
        var blue = (color & 0xFF) / 5;
        return (red << 16) | (green << 8) | blue;
    }

    private function colorProperty(key as String, fallback as Number) as Number {
        var value = Application.Properties.getValue(key);
        if (value instanceof Number) {
            return value as Number;
        }
        return fallback;
    }

    private function spaced(text as String) as String {
        var out = "";
        for (var index = 0; index < text.length(); index++) {
            if (index > 0) {
                out += " ";
            }
            out += text.substring(index, index + 1);
        }
        return out;
    }

    private function grouped(value as Number) as String {
        var text = value.format("%d");
        var out = "";
        var count = 0;
        for (var index = text.length() - 1; index >= 0; index--) {
            if (count == 3) {
                out = "," + out;
                count = 0;
            }
            out = text.substring(index, index + 1) + out;
            count += 1;
        }
        return out;
    }

    private function twoDigits(value as Number) as String {
        if (value < 10) {
            return "0" + value.format("%d");
        }
        return value.format("%d");
    }
}
