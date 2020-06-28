import ueberzug.lib.v0 as ueberzug
import sys
import time

if __name__ == '__main__' and len(sys.argv) > 3:
    with ueberzug.Canvas() as c:
        demo = c.create_placement(
            'demo', x=1, y=1,
            scaler=ueberzug.ScalerOption.COVER.value)
        demo.path = sys.argv[1]
        demo.visibility = ueberzug.Visibility.VISIBLE
        time.sleep(1)
