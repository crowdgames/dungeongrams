#[derive(Clone)]
pub struct Point {
    x: u8,
    y: u8
}

impl Point {
    pub fn new(x: u8, y: u8) -> Self {
        Self {x, y}
    }
}

impl PartialEq for Point {
    fn eq(&self, other: &Self) -> bool {
        self.x == other.x && self.y == other.y
    }
}

impl Eq for Point {}