use thiserror::Error;

#[derive(Debug, Error)]
pub enum Error {
    #[error(transparent)]
    IO(#[from] std::io::Error),
    #[error(transparent)]
    ColorCet(#[from] colorcet::ColorcetError),
    #[error("could not parse color: {0}")]
    ColorParse(String),
    #[error("could not covert ColorMap into LinearGradient")]
    Conversion,
}
