translate([-2, -226.6, 0]) linear_extrude(height=8, center=false, convexity=10) scale(4) import(file="LaserCut.dxf", layer="Unten");
translate([-156.6, -226.6, 231]) linear_extrude(height=8, center=false, convexity=10) scale(4) import(file="LaserCut.dxf", layer="Mitte");
translate([-311.2, -226.6, 282]) linear_extrude(height=8, center=false, convexity=10) scale(4) import(file="LaserCut.dxf", layer="Oben");
translate([8, -146, 0]) rotate([0, -90, 0]) linear_extrude(height=8, center=false, convexity=10) scale(4) import(file="LaserCut.dxf", layer="Links");
translate([147, 226.6, -290]) rotate([0, -90, 180]) linear_extrude(height=8, center=false, convexity=10) scale(4) import(file="LaserCut.dxf", layer="Rechts");
translate([155, 8, 0]) rotate([0, -90, 90]) linear_extrude(height=8, center=false, convexity=10) scale(4) import(file="LaserCut.dxf", layer="Vorne");
translate([0, 72.4, -290]) rotate([0, -90, -90]) linear_extrude(height=8, center=false, convexity=10) scale(4) import(file="LaserCut.dxf", layer="Hinten");

use <raspi3.scad>;
translate([113.5, 42, 240]) rotate([0, 0, 180]) color("blue") raspi3();