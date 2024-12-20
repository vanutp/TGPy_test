{ pkgs }:
self: super: {
  telethon-v1-24 = super.telethon.overridePythonAttrs (old: rec {
    version = "1.24.18";
    src = pkgs.fetchPypi {
      pname = "Telethon-v1.24";
      inherit version;
      hash = "sha256-rVgunqMHpOLjRhIZ7RfugTrrv136YtTlqa9CvWOyElY=";
    };
    doCheck = false;
  });
  cryptg-anyos = super.cryptg.overridePythonAttrs (old: rec {
    version = "0.4.1";
    src = super.fetchPypi {
      pname = "cryptg-anyos";
      inherit version;
      hash = "sha256-pXY0CfdZRDjgID78STTDrvm1wUj4z1AooUBtrSG09Qo=";
    };
    cargoDeps = pkgs.rustPlatform.fetchCargoTarball {
      inherit src;
      hash = "sha256-AqSVFOB9Lfvk9h3GtoYlEOXBEt7YZYLhCDNKM9upQ2U=";
    };
  });
  python-semantic-release = pkgs.callPackage ./python-semantic-release.nix { };
}
