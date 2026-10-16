import Toybox.Lang;
import Toybox.Test;

(:typecheck(strict))
module FluidaTests {

    (:test)
    function testMidnightAndNoonAreTwelve(logger as Test.Logger) as Boolean {
        Test.assertEqual(12, Clock.displayHour(0));
        Test.assertEqual(12, Clock.displayHour(12));
        Test.assertEqual(1, Clock.displayHour(13));
        Test.assertEqual(11, Clock.displayHour(23));
        return true;
    }

    (:test)
    function testHourFillBounds(logger as Test.Logger) as Boolean {
        var oneFill = Clock.hourFill(1);
        var twelveFill = Clock.hourFill(12);
        Test.assert(oneFill >= 0.0f && oneFill < 0.001f);
        Test.assert(twelveFill > 0.999f && twelveFill <= 1.0f);
        return true;
    }

    (:test)
    function testMinuteFillBounds(logger as Test.Logger) as Boolean {
        var zeroFill = Clock.minuteFill(0, 0);
        var endFill = Clock.minuteFill(59, 59);
        Test.assert(zeroFill == 0.0f);
        Test.assert(endFill > 0.98f && endFill < 1.0f);
        return true;
    }
}
