{
	description = "A flake for Streamlit development";

	inputs = {
		nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
		flake-utils.url = "github:numtide/flake-utils";
	};

	outputs = {nixpkgs, flake-utils, ...}:
	flake-utils.lib.eachDefaultSystem (system:
		let
		  pkgs = import nixpkgs { 
				inherit system; 
				config.allowUnfree = true;
			};
		in {
			devShells.default = pkgs.callPackage ./shell.nix { inherit pkgs; };
		});
}
