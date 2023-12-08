{ pkgs, git-cdn }:

pkgs.dockerTools.buildLayeredImage {
  name = "git-cdn-container";
  tag = "latest";

  enableFakechroot = true;
  fakeRootCommands = ''
    mkdir -p /data
  '';

  contents = [
    git-cdn
  ];

  config = {
    # Env = {
    #   GITSERVER_UPSTREAM="https://gitlab.com/";
    #   WORKING_DIRECTORY="/data";
    #   PORT="8000";
    # };
    # Entrypoint = [ ];
    WorkingDir = "/data";
    Cmd = [ "${git-cdn}/bin/git-cdn-start" ];
    Volumes = {
      "/data" = {};
    };
    ExposedPorts = {
      "8000/tcp" = {};
    };
  };

  maxLayers = 120;
}

### Steps
# nix build .#git-cdn-container
# gunzip -c ./result > git-cdn.container
# docker load --input ./git-cdn.container
# docker run --rm -it -e GITSERVER_UPSTREAM="https://gitlab.com/" -e WORKING_DIRECTORY="/cache" -e PORT=8000 git-cdn-container:latest
