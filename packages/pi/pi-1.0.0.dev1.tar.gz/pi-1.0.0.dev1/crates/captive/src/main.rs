use pishell_captive::main as captive_main;

pub fn main() -> Result<(), Box<dyn std::error::Error>> {
    captive_main(
        std::env::args()
            .collect::<Vec<_>>()
            .iter()
            .map(|s| s.as_str())
            .collect::<Vec<_>>()
            .as_slice(),
    )
}
