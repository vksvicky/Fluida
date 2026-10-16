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
    private var _sightHour as WatchUi.BitmapResource;
    private var _sightMinute as WatchUi.BitmapResource;
    (:mip)
    private var _plate as WatchUi.BitmapResource;
    (:amoled)
    private var _fontScale as WatchUi.FontResource;

    (:mip)
    function initialize() {
        WatchFace.initialize();
        _fontMetric = WatchUi.loadResource(Rez.Fonts.FaceMetric) as WatchUi.FontResource;
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
        _sightHour = WatchUi.loadResource(Rez.Drawables.fluid_sight_hour) as WatchUi.BitmapResource;
        _sightMinute = WatchUi.loadResource(Rez.Drawables.fluid_sight_minute) as WatchUi.BitmapResource;
        _plate = WatchUi.loadResource(Rez.Drawables.dial_bg) as WatchUi.BitmapResource;
    }

    (:amoled)
    function initialize() {
        WatchFace.initialize();
        _fontMetric = WatchUi.loadResource(Rez.Fonts.FaceMetric) as WatchUi.FontResource;
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
        _sightHour = WatchUi.loadResource(Rez.Drawables.fluid_sight_hour) as WatchUi.BitmapResource;
        _sightMinute = WatchUi.loadResource(Rez.Drawables.fluid_sight_minute) as WatchUi.BitmapResource;
        _fontScale = WatchUi.loadResource(Rez.Fonts.FaceScale) as WatchUi.FontResource;
    }

    function onUpdate(dc as Graphics.Dc) as Void {
        var width = dc.getWidth();
        var clock = System.getClockTime();
        var secondColor = colorProperty("SecondsFluidColor", 0x00EBFF);

        dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_BLACK);
        dc.clear();
        drawPlate(dc);
        drawColumn(dc, width, 55, Clock.hourFill(clock.hour), _fluidHour);
        drawColumn(dc, width, 185, Clock.minuteFill(clock.min, clock.sec), _fluidMinute);
        drawSight(dc, width, 55, _sightHour);
        drawSight(dc, width, 185, _sightMinute);
        drawSeconds(dc, width, clock.sec, secondColor);
        drawDate(dc, width);
        drawMetrics(dc, width);
    }

    (:mip)
    private function drawPlate(dc as Graphics.Dc) as Void {
        dc.drawBitmap(0, 0, _plate);
    }

    (:amoled)
    private function drawPlate(dc as Graphics.Dc) as Void {
        var width = dc.getWidth();
        var cx = at(width, 120);
        var radius = at(width, 118);
        dc.setColor(0x282828, Graphics.COLOR_TRANSPARENT);
        dc.fillCircle(cx, cx, radius);
        dc.setColor(0x60646A, Graphics.COLOR_TRANSPARENT);
        dc.setPenWidth(1);
        dc.drawCircle(cx, cx, radius);
        drawTubeChrome(dc, width, 55);
        drawTubeChrome(dc, width, 185);
        drawScale(dc, width);
        dc.setColor(0xE8EEF6, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, at(width, 28), _fontMonth, "F L U I D A", Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
        dc.setColor(0x4B5564, Graphics.COLOR_TRANSPARENT);
        dc.setPenWidth(at(width, 2));
        dc.drawCircle(cx, at(width, 66), at(width, 20));
    }

    private function drawColumn(dc as Graphics.Dc, width as Number, center as Number, fill as Float, sprite as WatchUi.BitmapResource) as Void {
        var top = at(width, 52);
        var bottom = at(width, 184);
        var columnHeight = bottom - top;
        var fluidHeight = (Math.round(fill * columnHeight.toFloat()) as Float).toNumber();
        if (fluidHeight > columnHeight) {
            fluidHeight = columnHeight;
        }
        if (fluidHeight < 1) {
            return;
        }
        var inset = at(width, 2);
        if (inset < 1) {
            inset = 1;
        }
        var innerLeft = at(width, center) - at(width, 21) / 2 + inset;
        var innerWidth = at(width, 21) - (inset * 2);
        var meniscus = at(width, 6);
        dc.setClip(innerLeft, top, innerWidth, columnHeight);
        dc.drawBitmap(innerLeft, bottom - fluidHeight - meniscus, sprite);
        dc.clearClip();
    }

    private function drawSight(dc as Graphics.Dc, width as Number, center as Number, sight as WatchUi.BitmapResource) as Void {
        var left = at(width, center) - at(width, 21) / 2;
        var columnWidth = at(width, 21);
        var bottom = at(width, 184);
        var mid = left + columnWidth / 2;
        var resW = columnWidth + at(width, 8);
        var resTop = bottom - at(width, 2);
        var sightX = at(width, 4);
        var sightY = at(width, 5);
        if (sightX < 1) {
            sightX = 1;
        }
        if (sightY < 1) {
            sightY = 1;
        }
        dc.drawBitmap(mid - resW / 2 + sightX, resTop + sightY, sight);
    }

    (:amoled)
    private function drawTubeChrome(dc as Graphics.Dc, width as Number, center as Number) as Void {
        var left = at(width, center) - at(width, 21) / 2;
        var top = at(width, 52);
        var columnWidth = at(width, 21);
        var height = at(width, 184) - top;
        var mid = left + (columnWidth / 2);
        var capW = columnWidth + at(width, 6);
        var capH = at(width, 14);
        dc.setColor(0x343A44, Graphics.COLOR_TRANSPARENT);
        dc.fillRoundedRectangle(mid - (capW / 2), top - capH, capW, capH, at(width, 4));
        var resW = columnWidth + at(width, 8);
        dc.fillRoundedRectangle(mid - (resW / 2), at(width, 184) - at(width, 2), resW, at(width, 25), at(width, 4));
        dc.setColor(0x0C1016, Graphics.COLOR_TRANSPARENT);
        dc.fillRoundedRectangle(left, top, columnWidth, height, at(width, 3));
    }

    (:amoled)
    private function drawScale(dc as Graphics.Dc, width as Number) as Void {
        var hourLeft = at(width, 55) - at(width, 21) / 2;
        var minuteRight = at(width, 185) - at(width, 21) / 2 + at(width, 21);
        var top = at(width, 52) + at(width, 6);
        var bottom = at(width, 184) - at(width, 6);
        var span = bottom - top;
        dc.setColor(0xECF2F8, Graphics.COLOR_TRANSPARENT);
        for (var hour = 1; hour <= 12; hour++) {
            var y = bottom - (Math.round(((hour - 1).toFloat() / 11.0f) * span.toFloat()) as Float).toNumber();
            dc.drawText(hourLeft - at(width, 10), y, _fontScale, hour.format("%d"), Graphics.TEXT_JUSTIFY_RIGHT | Graphics.TEXT_JUSTIFY_VCENTER);
        }
        for (var mark = 0; mark <= 60; mark += 10) {
            var y = bottom - (Math.round((mark.toFloat() / 60.0f) * span.toFloat()) as Float).toNumber();
            dc.drawText(minuteRight + at(width, 10), y, _fontScale, mark.format("%02d"), Graphics.TEXT_JUSTIFY_LEFT | Graphics.TEXT_JUSTIFY_VCENTER);
        }
    }

    private function drawSeconds(dc as Graphics.Dc, width as Number, second as Number, color as Number) as Void {
        var cx = at(width, 120);
        var cy = at(width, 66);
        var radius = at(width, 20);
        var radians = Math.toRadians((second * 6) - 90);
        var bx = cx + (Math.round(radius.toFloat() * Math.cos(radians)) as Float).toNumber();
        var by = cy + (Math.round(radius.toFloat() * Math.sin(radians)) as Float).toNumber();
        dc.setColor(darken(color), Graphics.COLOR_TRANSPARENT);
        dc.fillCircle(bx, by, at(width, 5));
        dc.setColor(color, Graphics.COLOR_TRANSPARENT);
        dc.fillCircle(bx, by, at(width, 3));
        dc.drawText(cx, cy, _fontSeconds, twoDigits(second), Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
    }

    private function drawDate(dc as Graphics.Dc, width as Number) as Void {
        var today = Gregorian.info(Time.now(), Time.FORMAT_SHORT);
        var month = today.month as Number;
        var day = today.day as Number;
        dc.setColor(0xA0ACB9, Graphics.COLOR_TRANSPARENT);
        dc.drawText(at(width, 120), at(width, 105), _fontMonth, spaced(_MONTHS[month - 1]), Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
        dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
        dc.drawText(at(width, 120), at(width, 120), _fontDate, day.format("%d"), Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
    }

    private function drawMetrics(dc as Graphics.Dc, width as Number) as Void {
        var stats = System.getSystemStats();
        var battery = (Math.round(stats.battery) as Float).toNumber();
        var stepsValue = ActivityMonitor.getInfo().steps;
        var stepsText = "--";
        if (stepsValue != null) {
            stepsText = grouped(stepsValue);
        }
        drawPair(dc, width, at(width, 88), at(width, 120), _iconHeart, "--", 0xF5F8FC, _fontMetric);
        drawPair(dc, width, at(width, 152), at(width, 120), _iconBattery, battery.format("%d") + "%", 0x00F07D, _fontMetric);
        drawPair(dc, width, at(width, 88), at(width, 148), _iconFlame, "--", 0xFF9128, _fontMetric);
        drawPair(dc, width, at(width, 152), at(width, 148), _iconTemp, "--", 0xFFD741, _fontMetric);
        drawPair(dc, width, at(width, 120), at(width, 178), _iconSteps, stepsText, 0x00EBFF, _fontMetric);
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
