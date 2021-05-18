use crate::point::Point;
use crate::state::State;
use crate::level::Level;

pub struct Game {
    loaded: bool,
    level: Level,
    state: State
}

fn collide_with_hazard(state: &State, point: &Point) -> bool {
    state.enemies.iter().any(|&point| point == new_position) &&
    state.spikes.iter().any(|&point| point == new_position)
}

fn valid_move_for_player(level: &Level, state: &State new_position: &Point) -> bool {
    if new_position == state.exit && state.switch_count > 0 {
        return false;
    }

    new_position >= 0 && 
    new_position.y >= 0 && 
    new_position.x < level.width && 
    new_position.y < level.height &&
    !level.blocks.contains(new_position)
}

fn valid_move_for_enemy(level: &Level, state: &State new_position: &Point) -> bool {
    if !valid_move_for_player(level, state, new_position) {
        return false
    }

    new_position != state.exit &&
    collide_with_hazard(state, new_position) &&
    state.switches.iter().any(|&point| point == new_position)
}

pub fn step -> State {
    unimplemented!("Game::step is not implemented");
}

impl Game {
    pub fn new() -> Self {
        Self {
            loaded: false,
            level: Level::new(),
            state: State::new()
        }
    }

    pub fn load {
        unimplemented!("Game::valid_move_for_player is not implemented");
    }

    pub fn display {
        unimplemented!("Game::valid_move_for_player is not implemented");
    }

}