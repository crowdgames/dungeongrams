use std::ops::Add;

#[derive(Clone)]
pub struct Point {
    pub x: u8,
    pub y: u8
}

impl Point {
    pub fn new(x: u8, y: u8) -> Self {
        Self {x, y}
    }
}


// Equality
impl PartialEq for Point {
    fn eq(&self, other: &Self) -> bool {
        self.x == other.x && self.y == other.y
    }
}

impl Eq for Point {}

// p1 + p2 overloading
impl Add for Point {
    type Output = Point;

    fn add(self, other: Point) -> Point {
        Point { x: self.x + other.x, y: self.y + other.y }
    }
}