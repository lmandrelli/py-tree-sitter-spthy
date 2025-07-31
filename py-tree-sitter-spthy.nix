{ lib
, buildPythonPackage
, fetchFromGitHub
, setuptools
, wheel
, tree-sitter
}:

let
  # Parse version from pyproject.toml
  pyproject = builtins.fromTOML (builtins.readFile ./pyproject.toml);
  version = pyproject.project.version;
in
buildPythonPackage rec {
  pname = "py-tree-sitter-spthy";
  inherit version;
  format = "pyproject";

  src = fetchFromGitHub {
    owner = "lmandrelli";
    repo = "py-tree-sitter-spthy";
    rev = "v${version}";
    hash = "sha256-CYDn36QUqDvuSLFSIHdKCtmkcmXJefiy35npNNnKzw4=";
  };

  nativeBuildInputs = [
    setuptools
    wheel
  ];

  propagatedBuildInputs = [
    tree-sitter
  ];

  # Skip tests - they require C compilation and grammar files
  doCheck = false;

  # Verify the package imports correctly
  pythonImportsCheck = [
    "py_tree_sitter_spthy"
  ];

  meta = with lib; {
    description = "Tree-sitter parser for Spthy language (Tamarin Prover)";
    homepage = "https://github.com/lmandrelli/py-tree-sitter-spthy";
    license = licenses.gpl3Plus;
    maintainers = [{
      name = "Luca Mandrelli";
      email = "luca.mandrelli@icloud.com";
      github = "lmandrelli";
    }];
    platforms = platforms.linux ++ platforms.darwin;
  };
}