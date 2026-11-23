fn main() {
    #[cfg(windows)]
    {
        use std::io::Write;
        // OPBro: la variante Admin empaqueta con otro icono; la ruta llega por
        // variable para no duplicar este build script.
        let icon = std::env::var("OPBRO_ICON")
            .unwrap_or_else(|_| "../../res/icon.ico".to_owned());
        println!("cargo:rerun-if-env-changed=OPBRO_ICON");
        let mut res = winres::WindowsResource::new();
        res.set_icon(&icon)
            .set_language(winapi::um::winnt::MAKELANGID(
                winapi::um::winnt::LANG_ENGLISH,
                winapi::um::winnt::SUBLANG_ENGLISH_US,
            ))
            .set_manifest_file("../../res/manifest.xml");
        match res.compile() {
            Err(e) => {
                write!(std::io::stderr(), "{}", e).unwrap();
                std::process::exit(1);
            }
            Ok(_) => {}
        }
    }
}
