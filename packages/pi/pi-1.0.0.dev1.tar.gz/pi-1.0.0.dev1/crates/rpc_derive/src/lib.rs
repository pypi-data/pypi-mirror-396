//! Procedural macros for Pi shell RPC interface registration
//!
//! This crate provides macros to automatically register RPC handlers
//! with the message server.

use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, punctuated::Punctuated, Item, ItemImpl, Lit, Meta, Token};

/// Attribute macro for registering RPC interface implementations
///
/// This macro automatically generates registration code for RPC handlers.
/// It should be applied to `impl` blocks that implement RPC interface traits.
///
/// # Usage
///
/// ```rust,ignore
/// #[rpc_interface(interface = "Shell")]
/// impl Shell for MyShellService {
///     fn terminal_info(&self, request: TerminalInfoRequest) -> Result<TerminalInfo, RpcError> {
///         // implementation
///     }
/// }
/// ```
///
/// This will generate message handler registration with
/// message_server.on_message.
#[proc_macro_attribute]
pub fn rpc_interface(args: TokenStream, input: TokenStream) -> TokenStream {
    let args = parse_macro_input!(args with Punctuated::<Meta, Token![,]>::parse_terminated);
    let input_item = parse_macro_input!(input as Item);

    // Parse the interface name from attributes
    let interface_name = extract_interface_name(&args)
        .unwrap_or_else(|| panic!("Missing 'interface' parameter in rpc_interface attribute"));

    match input_item {
        Item::Impl(impl_item) => {
            let expanded = generate_rpc_impl_registration(&interface_name, impl_item);
            TokenStream::from(expanded)
        }
        _ => {
            panic!("rpc_interface can only be applied to impl blocks");
        }
    }
}

/// Extract interface name from macro arguments
fn extract_interface_name(args: &Punctuated<Meta, Token![,]>) -> Option<String> {
    for arg in args {
        if let Meta::NameValue(nv) = arg {
            if nv.path.is_ident("interface") {
                if let syn::Expr::Lit(expr_lit) = &nv.value {
                    if let Lit::Str(lit_str) = &expr_lit.lit {
                        return Some(lit_str.value());
                    }
                }
            }
        }
    }
    None
}

/// Generate registration code for RPC interface implementations
fn generate_rpc_impl_registration(
    interface_name: &str,
    impl_item: ItemImpl,
) -> proc_macro2::TokenStream {
    let self_ty = &impl_item.self_ty;
    let impl_items = &impl_item.items;

    let mut handler_registrations = Vec::new();

    for item in impl_items {
        if let syn::ImplItem::Fn(method) = item {
            let method_name = &method.sig.ident;
            let method_name_str = method_name.to_string();
            let message_name = format!("{}:{}", interface_name, method_name_str);

            if let Some((request_type, _response_type)) = extract_method_types(&method.sig) {
                // Generate message handler registration
                let handler_registration = quote! {
                    {
                        let service_clone = service.clone();
                        message_server.on_message(
                            move |message: pishell_socket::messages::Message<#request_type>| -> Option<pishell_socket::messages::GenericMessage> {
                                let response = service_clone.#method_name(message.clone().payload);

                                match response {
                                    Ok(result) => {
                                        let response_msg = message.response(
                                            result,
                                        );
                                        Some(response_msg.into_generic())
                                    }
                                    Err(err) => {
                                        tracing::error!("RPC method {} failed: {}", #message_name, err);
                                        None
                                    }
                                }
                            },
                        );
                    }
                };

                handler_registrations.push(handler_registration);
            }
        }
    }

    quote! {
        #impl_item

        impl #self_ty {
            /// Register this RPC interface implementation with the message server
            pub fn register_rpc_handlers(
                service: std::sync::Arc<Self>,
                message_server: &pishell_socket::MessageServer,
            ) {
                use pishell_rpc_types::*;
                use pishell_rpc_types::messages::MessagePeer;

                // Register message handlers
                #(#handler_registrations)*
            }
        }
    }
}

/// Extract request and response types from a method signature
fn extract_method_types(sig: &syn::Signature) -> Option<(syn::Type, syn::Type)> {
    // Look for pattern: fn method_name(&self, request: RequestType) -> Result<ResponseType, RpcError>
    if sig.inputs.len() >= 2 {
        if let syn::FnArg::Typed(pat_type) = &sig.inputs[1] {
            let request_type = (*pat_type.ty).clone();

            // Extract response type from Result<ResponseType, RpcError>
            if let syn::ReturnType::Type(_, return_type) = &sig.output {
                if let syn::Type::Path(type_path) = return_type.as_ref() {
                    if let Some(segment) = type_path.path.segments.last() {
                        if segment.ident == "Result" {
                            if let syn::PathArguments::AngleBracketed(args) = &segment.arguments {
                                if let Some(syn::GenericArgument::Type(response_type)) =
                                    args.args.first()
                                {
                                    return Some((request_type, response_type.clone()));
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    None
}
