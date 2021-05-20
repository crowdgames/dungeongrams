use std::collections::HashSet;
use crate::point::Point;

pub struct Level {
    pub width: i8,
    pub height: i8,
    pub switch_count: i8,
    pub blocks: HashSet<Point>
}

impl Level {
    pub fn new() -> Self {
        Self {
            width: 0,
            height: 0,
            switch_count: 0,
            blocks: HashSet::new()
        }
    }
}