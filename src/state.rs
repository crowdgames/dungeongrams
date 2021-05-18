use crate::point::Point;
use crate::utility::point_vectors_equal;

#[derive(Clone)]
pub struct State {
    pub player: Point,
    pub exit: Point,
    pub enemies: Vec<Point>,
    pub enemies_origin: Vec<Point>,
    pub enemies_move: bool,
    pub spikes: Vec<Point>,
    pub switches: Vec<Point>,
    pub did_win: bool,
    pub did_lose: bool
}

impl State {
    pub fn new(player: Point, exit: Point) -> Self {
        Self {
            player: player,
            exit: exit,
            enemies: Vec::new(),
            enemies_origin: Vec::new(),
            enemies_move: false,
            spikes: Vec::new(),
            switches: Vec::new(),
            did_win: false,
            did_lose: false
        }
    }
}

impl PartialEq for State {
    fn eq(&self, other: &Self) -> bool {
        self.player == other.player && 
        self.exit == other.exit && 
        point_vectors_equal(&self.enemies, &other.enemies) &&
        point_vectors_equal(&self.enemies_origin, &other.enemies_origin) &&
        self.enemies_move == other.enemies_move &&
        point_vectors_equal(&self.spikes, &other.spikes) &&
        point_vectors_equal(&self.switches, &other.switches) &&
        self.did_win == other.did_win &&
        self.did_lose == other.did_lose
    }
}

impl Eq for State {}