import Toybox.Lang;

(:typecheck(strict))
class Clock {

    static function displayHour(hour as Number) as Number {
        var shown = hour % 12;
        if (shown == 0) {
            return 12;
        }
        return shown;
    }

    static function hourFill(hour as Number) as Float {
        return (displayHour(hour) - 1).toFloat() / 11.0f;
    }

    static function minuteFill(minute as Number, second as Number) as Float {
        return (minute.toFloat() + (second.toFloat() / 60.0f)) / 60.0f;
    }
}
