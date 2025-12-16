use quote::{format_ident, quote};
use std::{collections::BTreeMap, env, fs, path::Path, path::PathBuf, process::Command};
use typify::{TypeSpace, TypeSpaceSettings};

/// Configuration for RPC trait generation
#[derive(Debug, Clone)]
struct RpcConfig {}

impl RpcConfig {
    fn from_cargo_features() -> Self {
        Self {}
    }
}

fn find_pi_src_root() -> Option<PathBuf> {
    match std::env::var("_PI_SRC_ROOT") {
        Ok(v) => Some(PathBuf::from(v)),
        Err(_) => env::current_dir()
            .ok()
            .and_then(|dir| dir.parent().map(|p| p.to_path_buf()))
            .and_then(|dir| dir.parent().map(|p| p.to_path_buf())),
    }
}

fn find_python() -> Option<PathBuf> {
    if let Ok(pyo3_python) = env::var("PYO3_PYTHON").map(PathBuf::from) {
        Some(pyo3_python)
    } else {
        which::which("python3").ok()
    }
}

/// Build the command to generate the RPC schema
fn build_python_command() -> Command {
    let mut command = if let Some(python) = find_python() {
        println!("cargo::warning=Using {python:?} to generate schema");
        Command::new(python)
    } else {
        println!("cargo::warning=Using `uv run python` to generate schema");
        let mut cmd = Command::new("uv");
        cmd.args(["run"]);
        // Skip maturin entirely to avoid deadlocking build recursion
        // it is also quite a bit faster of course.
        cmd.env("_PI_BUILD_BACKEND", "uv_build");
        cmd
    };

    command.args([
        "-m",
        "pi._internal.build.rpc_schema",
        "--interfaces=pi._internal.protocols",
        "--rust-crate",
        env!("CARGO_PKG_NAME"),
        "--rust-crate-version",
        env!("CARGO_PKG_VERSION"),
    ]);

    command
}

/// Execute the schema generation command and handle errors
fn execute_schema_generation(mut command: Command) -> std::process::Output {
    let root = find_pi_src_root();

    let output = command
        .current_dir(root.unwrap_or(PathBuf::new()))
        .env("PYTHONIOENCODING", "utf-8")
        .output()
        .expect("could not execute Python to generate RPC schema");

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        panic!("Python schema generation failed: {stderr}");
    }

    output
}

/// Parse the JSON output from schema generation
fn parse_schema_output(output: std::process::Output) -> (String, Vec<String>) {
    let stdout = String::from_utf8(output.stdout).expect("non-utf8 stdout from Python");
    let payload: serde_json::Value = serde_json::from_str(&stdout)
        .unwrap_or_else(|e| panic!("invalid JSON from Python: {e}: {stdout}"));

    let schema = payload
        .get("schema")
        .and_then(|v| v.as_str())
        .expect("Python payload missing 'schema'")
        .to_string();

    let sources: Vec<String> = payload
        .get("sources")
        .and_then(|v| v.as_array())
        .expect("Python payload missing 'sources'")
        .iter()
        .filter_map(|v| v.as_str().map(|s| s.to_string()))
        .collect();

    (schema, sources)
}

fn get_schema() -> (String, Vec<String>) {
    let command = build_python_command();
    let output = execute_schema_generation(command);
    parse_schema_output(output)
}

fn generate_module_type_path(
    type_name: &str,
    schema: &serde_json::Value,
) -> proc_macro2::TokenStream {
    let (module_name, demangled_name) = demangle_type_name(type_name, schema);

    if module_name.is_empty() {
        let ident = syn::Ident::new(type_name, proc_macro2::Span::call_site());
        quote! { crate::__generated::#ident }
    } else {
        // Convert module name to lowercase for Rust module naming conventions
        let module_ident = syn::Ident::new(&module_name, proc_macro2::Span::call_site());
        let type_ident = syn::Ident::new(&demangled_name, proc_macro2::Span::call_site());
        quote! { #module_ident::#type_ident }
    }
}

/// Try simple demangling using "__" separator
fn try_simple_demangle(mangled_name: &str) -> Option<(String, String)> {
    if let Some(pos) = mangled_name.find("__") {
        let module = &mangled_name[..pos];
        let type_name = &mangled_name[pos + 2..];
        Some((module.to_string(), type_name.to_string()))
    } else {
        None
    }
}

/// Try complex demangling using schema information
fn try_schema_demangle(mangled_name: &str, schema: &serde_json::Value) -> Option<(String, String)> {
    let defs = schema.get("$defs")?;

    // Look through schema definitions to find matching x-rust-type path
    for (_def_name, def_value) in defs.as_object()? {
        let rust_type = def_value.get("x-rust-type")?;
        let path = rust_type.get("path")?.as_str()?;

        // Parse path like "pishell-rpc-types::Captive::CommandRequest"
        let path_parts: Vec<&str> = path.split("::").collect();
        if path_parts.len() >= 3 {
            let module = path_parts[path_parts.len() - 2];
            let expected_type = path_parts[path_parts.len() - 1];

            // Check if the mangled_name matches the pattern Module + Type
            // e.g., "CaptiveCommandRequest" should match module="Captive", type="CommandRequest"
            if mangled_name.starts_with(module) && mangled_name.len() > module.len() {
                let remaining = &mangled_name[module.len()..];
                if remaining == expected_type {
                    return Some((module.to_string(), expected_type.to_string()));
                }
            }
        }
    }

    None
}

fn demangle_type_name(mangled_name: &str, schema: &serde_json::Value) -> (String, String) {
    // Try simple demangling first
    if let Some(result) = try_simple_demangle(mangled_name) {
        return result;
    }

    // Try schema-based demangling
    if let Some(result) = try_schema_demangle(mangled_name, schema) {
        return result;
    }

    // Fallback to empty module if no schema information found
    (String::new(), mangled_name.to_string())
}

fn parse_schema_and_interfaces(
    schema_content: &str,
) -> (
    serde_json::Value,
    serde_json::Map<String, serde_json::Value>,
) {
    let schema: serde_json::Value = serde_json::from_str(schema_content).unwrap();

    let interfaces = schema
        .get("properties")
        .and_then(|p| p.get("interfaces"))
        .and_then(|i| i.as_object())
        .cloned()
        .unwrap_or_default();

    (schema, interfaces)
}

/// Collect types that need to be aliased into modules
fn collect_type_aliases(
    file: &syn::File,
    schema: &serde_json::Value,
) -> BTreeMap<String, Vec<(String, String)>> {
    let mut module_aliases: BTreeMap<String, Vec<(String, String)>> = BTreeMap::new();

    for item in &file.items {
        let type_name = match item {
            syn::Item::Struct(item_struct) => item_struct.ident.to_string(),
            syn::Item::Enum(item_enum) => item_enum.ident.to_string(),
            syn::Item::Type(item_type) => item_type.ident.to_string(),
            _ => continue,
        };

        let (module_name, demangled_name) = demangle_type_name(&type_name, schema);

        if !module_name.is_empty() {
            module_aliases
                .entry(module_name.to_string())
                .or_insert_with(Vec::new)
                .push((demangled_name.to_string(), type_name));
        }
    }

    module_aliases
}

/// Generate trait methods for a single interface method
fn generate_trait_method(
    method_name: &str,
    method_def: &serde_json::Value,
    schema: &serde_json::Value,
    _config: &RpcConfig,
) -> Option<(
    proc_macro2::TokenStream,
    proc_macro2::TokenStream,
    proc_macro2::TokenStream,
)> {
    let method_ident = syn::Ident::new(method_name, proc_macro2::Span::call_site());

    let request_ref = method_def
        .get("properties")?
        .get("request")?
        .get("$ref")?
        .as_str()?;

    let request_type_name = request_ref.strip_prefix("#/$defs/").unwrap_or(request_ref);

    // Use the module-namespaced path for types
    let request_type = generate_module_type_path(request_type_name, schema);

    // Handle optional response - if missing, use unit type ()
    let response_type = if let Some(response_ref) = method_def
        .get("properties")
        .and_then(|p| p.get("response"))
        .and_then(|r| r.get("$ref"))
        .and_then(|r| r.as_str())
    {
        let response_type_name = response_ref
            .strip_prefix("#/$defs/")
            .unwrap_or(response_ref);
        generate_module_type_path(response_type_name, schema)
    } else {
        quote! { () }
    };

    let trait_method = quote! {
        fn #method_ident(
            &self,
            request: #request_type,
        ) -> Result<#response_type, crate::RpcError>;
    };

    let client_method = quote! {
        pub fn #method_ident<F>(
            &mut self,
            request: #request_type,
            receiver: Option<&str>,
            callback: F,
        ) -> Result<(), crate::RpcError>
        where
            F: Fn(Result<#response_type, crate::RpcError>) + Send + Sync + 'static,
        {
            self.send_request(#method_name, receiver, request, callback)
        }
    };

    let broadcast_method_ident = format_ident!("{}_broadcast", method_ident);
    let client_broadcast_method = quote! {
        pub fn #broadcast_method_ident(
            &self,
            request: #request_type,
        ) -> Result<(), crate::RpcError>
        {
            self.send_broadcast(#method_name, request)
        }
    };

    Some((trait_method, client_method, client_broadcast_method))
}

/// Collect all message types (Request/Response) from interfaces with
/// their corresponding method names for MessageType trait
/// implementations.
fn collect_message_types(
    interfaces: &serde_json::Map<String, serde_json::Value>,
    schema: &serde_json::Value,
) -> Vec<(String, String, String)> {
    let mut message_types = Vec::new();

    for (interface_name, interface_def) in interfaces {
        if let Some(properties) = interface_def.get("properties").and_then(|p| p.as_object()) {
            for (method_name, method_def) in properties {
                // Collect request type
                if let Some(request_ref) = method_def
                    .get("properties")
                    .and_then(|p| p.get("request"))
                    .and_then(|r| r.get("$ref"))
                    .and_then(|r| r.as_str())
                {
                    let request_type_name =
                        request_ref.strip_prefix("#/$defs/").unwrap_or(request_ref);
                    let (module_name, demangled_name) =
                        demangle_type_name(request_type_name, schema);
                    if !module_name.is_empty() {
                        message_types.push((
                            module_name.clone(),
                            demangled_name,
                            format!("{}:{}", interface_name, method_name),
                        ));
                    }
                }

                // Collect response type
                if let Some(response_ref) = method_def
                    .get("properties")
                    .and_then(|p| p.get("response"))
                    .and_then(|r| r.get("$ref"))
                    .and_then(|r| r.as_str())
                {
                    let response_type_name = response_ref
                        .strip_prefix("#/$defs/")
                        .unwrap_or(response_ref);
                    let (module_name, demangled_name) =
                        demangle_type_name(response_type_name, schema);
                    if !module_name.is_empty() {
                        message_types.push((
                            module_name.clone(),
                            demangled_name,
                            format!("{}:{}", interface_name, method_name),
                        ));
                    }
                }
            }
        }
    }

    message_types
}

/// Generate explicit MessageType implementations for RPC message types.
fn generate_message_type_impls(
    message_types: Vec<(String, String, String)>,
) -> proc_macro2::TokenStream {
    let mut impls = Vec::new();

    for (module_name, type_name, message_name) in message_types {
        let module_ident = syn::Ident::new(&module_name, proc_macro2::Span::call_site());
        let type_ident = syn::Ident::new(&type_name, proc_macro2::Span::call_site());

        let impl_block = quote! {
            impl crate::messages::MessageType for #module_ident::#type_ident {
                fn message_type_name(&self) -> &'static str {
                    #message_name
                }

                fn to_json(&self) -> serde_json::Value {
                    serde_json::to_value(self).unwrap()
                }
            }

            impl crate::messages::MessageTypeStatic for #module_ident::#type_ident {
                fn message_type_name() -> &'static str {
                    #message_name
                }
            }
        };

        impls.push(impl_block);
    }

    quote! {
        #(#impls)*
    }
}

/// Generate traits and clients for all interfaces
fn generate_interface_traits(
    interfaces: serde_json::Map<String, serde_json::Value>,
    schema: &serde_json::Value,
    config: &RpcConfig,
) -> BTreeMap<String, proc_macro2::TokenStream> {
    let mut interface_traits: BTreeMap<String, proc_macro2::TokenStream> = BTreeMap::new();

    for (interface_name, interface_def) in &interfaces {
        let module_name = interface_name.to_owned();
        let mut trait_methods = Vec::new();
        let mut client_methods = Vec::new();

        if let Some(properties) = interface_def.get("properties").and_then(|p| p.as_object()) {
            for (method_name, method_def) in properties {
                if let Some((trait_method, client_method, client_broadcast_method)) =
                    generate_trait_method(method_name, method_def, schema, config)
                {
                    trait_methods.push(trait_method);
                    client_methods.push(client_method);
                    client_methods.push(client_broadcast_method);
                }
            }
        }

        let trait_content =
            generate_interface_trait_content(interface_name, trait_methods, client_methods, config);

        interface_traits.insert(module_name, trait_content);
    }

    interface_traits
}

/// Generate the complete trait content for an interface
fn generate_interface_trait_content(
    interface_name: &str,
    trait_methods: Vec<proc_macro2::TokenStream>,
    client_methods: Vec<proc_macro2::TokenStream>,
    _config: &RpcConfig,
) -> proc_macro2::TokenStream {
    quote! {
        /// RPC service trait for this interface
        pub trait Service: Send + Sync {
            #(#trait_methods)*
        }

        /// Registration helper for this interface
        ///
        /// This struct provides methods for registering RPC handlers
        /// with the message server. It is implemented by the procedural macro.
        pub struct Registration;

        /// Client implementation for the #interface_name RPC interface
        #[derive(Debug, Clone)]
        pub struct Client<P>
        where
            P: crate::messages::MessagePeer,
        {
            message_server: P,
        }

        impl<P> Client<P>
        where
            P: crate::messages::MessagePeer,
        {
            /// Create a new RPC client with the given message server
            pub fn new(message_server: P) -> Self {
                Self { message_server }
            }

            /// Send an RPC request with a callback for handling the response
            /// Returns immediately after sending the request
            pub fn send_request<Req, Resp, F>(
                &mut self,
                method_name: &str,
                receiver: Option<&str>,
                request: Req,
                callback: F,
            ) -> Result<(), crate::RpcError>
            where
                Req: crate::messages::MessageType + serde::Serialize,
                Resp: crate::messages::MessageTypeStatic + serde::de::DeserializeOwned + Clone + 'static,
                F: Fn(Result<Resp, crate::RpcError>) + Send + Sync + 'static,
            {
                // Set up response handler with callback
                self.message_server.on_message::<Resp, _>(move |message: crate::messages::Message<Resp>| {
                    tracing::debug!("RPC client received response for {}", #interface_name);
                    callback(Ok(message.payload.clone()));
                    None
                });

                // Send the request using the message server
                let receiver_name = receiver.as_deref().unwrap_or("broadcast");
                self.message_server.send_message(receiver_name, request)
                    .map_err(|e| crate::RpcError::Rpc(
                        format!("Failed to send RPC request {}:{} - {}", #interface_name, method_name, e)
                    ))?;

                tracing::debug!("Sent RPC request {}:{} to {}", #interface_name, method_name, receiver_name);
                Ok(())
            }

            /// Send an RPC broadcast
            pub fn send_broadcast<Req>(
                &self,
                method_name: &str,
                request: Req,
            ) -> Result<(), crate::RpcError>
            where
                Req: crate::messages::MessageType + serde::Serialize
            {
                // Send the request using the message server
                self.message_server.send_message("broadcast", request)
                    .map_err(|e| crate::RpcError::Rpc(
                        format!("Failed to send RPC broadcast {}:{} - {}", #interface_name, method_name, e)
                    ))?;

                tracing::debug!("Sent RPC broadcast {}:{}", #interface_name, method_name);
                Ok(())
            }

            #(#client_methods)*
        }
    }
}

fn generate_module_content(
    module_aliases: BTreeMap<String, Vec<(String, String)>>,
    mut interface_traits: BTreeMap<String, proc_macro2::TokenStream>,
) -> Vec<proc_macro2::TokenStream> {
    let mut alias_modules = Vec::new();

    // Handle modules that have both types and traits
    for (module_name, aliases) in &module_aliases {
        let module_ident = syn::Ident::new(module_name, proc_macro2::Span::call_site());
        let mut alias_items = Vec::new();

        for (alias_name, original_name) in aliases {
            let alias_ident = syn::Ident::new(alias_name, proc_macro2::Span::call_site());
            let original_ident = syn::Ident::new(original_name, proc_macro2::Span::call_site());
            alias_items.push(quote! {
                pub use crate::__generated::#original_ident as #alias_ident;
            });
        }

        // Include trait definitions if they exist for this module
        let trait_content = interface_traits
            .remove(module_name)
            .unwrap_or_else(|| quote! {});

        let module_content = quote! {
            #[allow(non_snake_case)]
            pub mod #module_ident {
                use crate::*;

                #(#alias_items)*

                #trait_content
            }
        };

        alias_modules.push(module_content);
    }

    // Add modules for interfaces that don't have types
    for (module_name, trait_content) in interface_traits {
        let module_ident = syn::Ident::new(&module_name, proc_macro2::Span::call_site());
        let module_content = quote! {
            #[allow(non_snake_case)]
            pub mod #module_ident {
                use crate::*;

                #trait_content
            }
        };
        alias_modules.push(module_content);
    }

    alias_modules
}

/// Assemble the final output with all generated code
fn assemble_final_output(
    file: &syn::File,
    alias_modules: Vec<proc_macro2::TokenStream>,
    message_type_impls: proc_macro2::TokenStream,
) -> proc_macro2::TokenStream {
    // Put all typify-generated types in a private module
    let items = &file.items;
    let generated_module = quote! {
        mod __generated {
            #(#items)*
        }
    };

    quote! {
        #generated_module

        /// Error type for RPC operations
        #[derive(Debug, thiserror::Error)]
        pub enum RpcError {
            #[error("Serialization error: {0}")]
            Serialization(#[from] serde_json::Error),
            #[error("IO error: {0}")]
            Io(#[from] std::io::Error),
            #[error("RPC error: {0}")]
            Rpc(String),
        }

        #(#alias_modules)*

        #message_type_impls
    }
}

fn generate_unified_types_and_traits(
    type_space: &TypeSpace,
    schema_content: &str,
    config: &RpcConfig,
) -> String {
    let tokens = type_space.to_stream();
    let (schema, interfaces) = parse_schema_and_interfaces(schema_content);

    let file = syn::parse2::<syn::File>(tokens).unwrap();

    let module_aliases = collect_type_aliases(&file, &schema);
    let interface_traits = generate_interface_traits(interfaces.clone(), &schema, config);
    let alias_modules = generate_module_content(module_aliases, interface_traits);

    let message_types = collect_message_types(&interfaces, &schema);
    let message_type_impls = generate_message_type_impls(message_types);

    let final_output = assemble_final_output(&file, alias_modules, message_type_impls);

    prettyplease::unparse(&syn::parse2::<syn::File>(final_output).unwrap())
}

fn main() {
    let (content, sources) = get_schema();
    for src in sources {
        println!("cargo::rerun-if-changed={src}");
    }
    let mut out_file = Path::new(&env::var("OUT_DIR").unwrap()).to_path_buf();
    out_file.push("schema.json");
    fs::write(out_file, &content).unwrap();

    let schema = serde_json::from_str::<schemars::schema::RootSchema>(&content).unwrap();

    let mut type_space = TypeSpace::new(
        TypeSpaceSettings::default()
            .with_struct_builder(true)
            .with_unknown_crates(typify::UnknownPolicy::Allow),
    );
    type_space.add_root_schema(schema).unwrap();

    // Generate unified types and traits
    let config = RpcConfig::from_cargo_features();
    let contents = generate_unified_types_and_traits(&type_space, &content, &config);

    let mut out_file = Path::new(&env::var("OUT_DIR").unwrap()).to_path_buf();
    out_file.push("rpc_types.rs");
    fs::write(out_file, &contents).unwrap();
}
