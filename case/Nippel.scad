module nippel() {
    kd=35;
    intersection() {
        translate([0, 0, 12.6-kd/2]) sphere(d=kd, $fn=64);
        union() {
            cylinder(d=9, h=0.6, $fn=64);
            translate([0, 0, 0.6]) cylinder(d1=5, d2=7, h=3, $fn=64);
            translate([0, 0, 3.6]) cylinder(d=7, h=kd, $fn=64);
        }
    }
}

difference() {
    nippel();
    translate([-3.3, -3.7, 12.6-0.8]) linear_extrude(height=2) text("+", font="Liberation Sans", size=8);
}

translate([10, 0, 0]) difference() {
    nippel();
    translate([-2.3, -3.7, 12.6-0.8]) linear_extrude(height=2) text("-", font="Liberation Sans", size=10);
}

translate([20, 0, 0]) difference() {
    nippel();
    translate([-2.75, -7.8, 12.6-0.8]) linear_extrude(height=2) text("°", font="Liberation Sans", size=10);
}