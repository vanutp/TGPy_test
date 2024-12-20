{
  lib,
  fetchFromGitHub,
  python3Packages,
}:

python3Packages.buildPythonApplication rec {
  pname = "python-semantic-release";
  version = "9.15.2";
  pyproject = true;

  src = fetchFromGitHub {
    owner = "python-semantic-release";
    repo = "python-semantic-release";
    rev = "v${version}";
    hash = "sha256-raHqbnD/gKNhhzACJfrKdeo4lSQVg3/vZz6inMPZgnM=";
  };

  postPatch = ''
    substituteInPlace pyproject.toml --replace-fail "setuptools ~= 75.3.0" "setuptools"
  '';

  build-system = with python3Packages; [
    setuptools
    wheel
  ];

  dependencies = with python3Packages; [
    click
    click-option-group
    gitpython
    requests
    jinja2
    python-gitlab
    tomlkit
    dotty-dict
    importlib-resources
    pydantic
    rich
    shellingham
    setuptools
  ];

  doCheck = false;

  meta = with lib; {
    description = "Automatic Semantic Versioning for Python projects";
    homepage = "https://python-semantic-release.readthedocs.io";
    changelog = "https://github.com/python-semantic-release/python-semantic-release/blob/master/CHANGELOG.md";
    license = licenses.mit;
    maintainers = [ ]; # Add maintainers if needed
  };
}
