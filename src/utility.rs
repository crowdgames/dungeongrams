use crate::point::Point;

pub fn point_vectors_equal(vec_a: &Vec<Point>, vec_b: &Vec<Point>) -> bool {
    vec_a.len() == vec_b.len() && vec_a.iter().zip(vec_b).all(|(a, b)| a == b)
}