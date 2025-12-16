
# keyboardestop

Reusable emergency stop helpers for CoDrone EDU (and similar Python drone SDKs).

## Quick Start
```python
from codrone_edu.drone import Drone
import keyboardestop as kes

drone = Drone()
drone.pair("COM4")
kes.install(drone)  # Ctrl+C will call emergency_stop() and exit by default

drone.takeoff()
drone.hover(5.0)
drone.land()
