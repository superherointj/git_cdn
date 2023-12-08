{ pkgs
, poetry2nix
}:

let
  app = poetry2nix.mkPoetryApplication {
    projectDir = ./.;
    postPatch = ''
      substituteInPlace pyproject.toml \
        --replace poetry.masonry.api poetry.core.masonry.api \
        --replace "poetry>=" "poetry-core>="
    '';
  };
in
  pkgs.writeShellApplication {
    runtimeInputs = [ app.dependencyEnv ];
    name = "git-cdn-start";
    text = ''
      [[ ! -v GITSERVER_UPSTREAM ]] && echo "ERROR: Environment variable GITSERVER_UPSTREAM is not defined." && echo "Like: GITSERVER_UPSTREAM=https://gitlab.com/" && exit 1
      [[ ! -v WORKING_DIRECTORY ]] && echo "ERROR: Environment variable WORKING_DIRECTORY is not defined." && echo "Like: WORKING_DIRECTORY=\''$HOME/.cache/git-cdn" && exit 1

      ${app.dependencyEnv}/bin/gunicorn git_cdn.app:app -c ${./config.py} "$@"
    '';
  }
