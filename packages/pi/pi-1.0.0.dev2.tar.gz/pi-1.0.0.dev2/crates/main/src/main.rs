mod cli;

pub fn main() {
    cli::main(
        std::env::args()
            .collect::<Vec<_>>()
            .iter()
            .map(|s| s.as_str())
            .collect(),
    );
}
