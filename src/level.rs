use std::collections::HashSet;
use crate::point::Point;

pub struct Level {
    width: u8,
    height: u8,
    switch_count: u8,
    blocks: HashSet<Point>
}
