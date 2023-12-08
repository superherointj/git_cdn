{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    poetry2nix.url = "github:nix-community/poetry2nix";
    #poetry2nix.url = "github:superherointj/poetry2nix";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, flake-utils, poetry2nix, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ poetry2nix.overlays.default ];
        };
      in
      {
        packages = rec {
          git-cdn-manual = pkgs.callPackage ./default-manual.nix { };
          git-cdn-poetry = pkgs.callPackage ./default-poetry.nix { };
          git-cdn-container = pkgs.callPackage ./default-container.nix {
            inherit git-cdn;
          };
          git-cdn = git-cdn-poetry;
          default = git-cdn;
        };
        apps = rec {
          git-cdn = flake-utils.lib.mkApp { drv = self.packages.${system}.git-cdn; };
          default = git-cdn;
        };
      }
    );
}
