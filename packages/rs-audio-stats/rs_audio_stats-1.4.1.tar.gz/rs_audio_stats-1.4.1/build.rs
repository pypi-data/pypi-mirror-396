use std::env;

fn main() {
    let target = env::var("TARGET").unwrap_or_default();
    
    // Only apply MSVC-specific flags when actually targeting MSVC
    if target.contains("msvc") {
        println!("cargo:rustc-link-arg=/LTCG");
        println!("cargo:rustc-link-arg=/OPT:REF");
        println!("cargo:rustc-link-arg=/OPT:ICF");
    }
    
    // For GNU targets, do nothing special
    println!("cargo:rerun-if-changed=build.rs");
}