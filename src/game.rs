use crate::point::Point;
use crate::state::State;
use crate::level::Level;

pub struct Game {
    loaded: bool,
    level: Level,
    state: State
}

fn collide_with_hazard(state: &State, point: &Point) -> bool {
    state.enemies.iter().any(|new_point| point == new_point) &&
    state.spikes.iter().any(|new_point| point == new_point)
}

fn valid_move_for_player(level: &Level, state: &State, new_position: &Point) -> bool {
    if new_position == &state.exit && state.switches.len() > 0 {
        return false;
    }

    new_position.x >= 0 && 
    new_position.y >= 0 && 
    new_position.x < level.width && 
    new_position.y < level.height &&
    !level.blocks.contains(new_position)
}

fn valid_move_for_enemy(level: &Level, state: &State, new_position: &Point) -> bool {
    if !valid_move_for_player(level, state, new_position) {
        return false
    }

    new_position != &state.exit &&
    collide_with_hazard(state, new_position) &&
    state.switches.iter().any(|point| point == new_position)
}



pub fn step(level: &Level, old_state: &State, action: &str) -> State {
    let dir: Point;
    match action {
        "" => dir = Point::new(0,0),
        "w" => dir = Point::new(-1,0),
        "s" => dir = Point::new(1,0),
        "a" => dir = Point::new(0,-1),
        "d" => dir = Point::new(0,01),
        _ => unimplemented!("{} not handled", action)
    }

    let state = old_state.clone();
    let next_position = state.player + dir;

    if valid_move_for_player(next_position) {
        state.player = next_position; 
    }

    if collide_with_hazard(state, state.player) {
        state.did_lose = true;
    } else if state.player == state.exit {
        state.did_win = true;
    } else {
        let contains
    }

    // pnrc = Game.validmoveforplayer(level, newstate, newstate.player, pdr, pdc)
    // if pnrc:
    //     newstate.player = pnrc

    // if Game.playercollidehazard(level, newstate):
    //     newstate.didlose = True
        
    // elif newstate.player == newstate.exit:
    //     newstate.didwin = True

    // elif newstate.player in newstate.switches:
    //     del newstate.switches[newstate.switches.index(newstate.player)]


    new_state
}

impl Game {
    pub fn new() -> Self {
        Self {
            loaded: false,
            level: Level::new(),
            state: State::new()
        }
    }

    pub fn load() {
        unimplemented!("Game::valid_move_for_player is not implemented");
    }

    pub fn display() {
        unimplemented!("Game::valid_move_for_player is not implemented");
    }

}