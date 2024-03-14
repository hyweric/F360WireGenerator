# 📜 Description

Automatically generates wires in Fusion 360. 

No more tedious splines or tricky 3D sketches. With this tool, simply select your start and end points, input your parameters, and the program generates several spline variations. Select the right one for your fit, and easily adjust by changing the spline points.  

# 🧑‍🏫 Demo
<aside>

https://github.com/yeetric/F360WireGenerator/assets/82407170/346ee334-fdef-468a-a715-5cdb678d55a2

</aside>

# 🗝️ Parameters

- **Start point:** Starting point of the wire, must be create on the same sketch as the end point, even if it is a 3D sketch
- **End point:** Ending point of the wire ****
- **Plane:** plane on which your sketch (2D or 3D) was created, that contains both the start and end points
- **Number of Points:** Number of points to be generated other than selected start-end points
- **Wire Radius:** Radius of wire that is going to be generated
- **Spread:** The Spread of the points that are going to be generated for a spline
- **Iterations:** Number of spline variations generated
- **Angle:** Adjust the angle of the wire generated ——  may depend on coordinate axis of your sketch
- **Angle Variance:** Deviation of the angle  —— Scalar of preset value (not exactly degrees but close)
- **Distance from Midpoint:** Perpendicular distance of the generated spline points from the Start-end line midpoint —— Scalar of preset value, not based on mm)
- **Disable Sweep:** Activating Disable sweep will only generate the spline and not perform the sweep path motion that creates the body

# Diagram

<img src="https://github.com/yeetric/F360WireGenerator/assets/82407170/93a1e2e3-5623-49a5-831a-87d923fd50e1" width="50%">
