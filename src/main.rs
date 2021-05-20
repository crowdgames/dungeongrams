mod config;
mod point;
mod utility;
mod level;
mod state;
mod game;

use state::State;
use point::Point;

fn main() {
    println!("Hello, world! {}", config::FLAW_NO_SPEED);
}
