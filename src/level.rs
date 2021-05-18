use std::collections::HashSet;
use crate::point::Point;

pub struct Level {
    width: u8,
    height: u8,
    switch_count: u8,
    blocks: HashSet<Point>
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