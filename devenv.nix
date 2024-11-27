{ pkgs, lib, config, inputs, ... }:

{
  env.OGRODJE_OBSERVER_ENV = "development";
  env.KT_BROKERS = "localhost:9092";

  packages = [ 
    pkgs.python311Packages.pip
    pkgs.python311Full
	pkgs.jq
	pkgs.kcat
	pkgs.kt
	pkgs.entr
	pkgs.nodePackages.nodemon
  ];

  languages.python.uv.enable = true;
  languages.python = {
	 enable = true;
	 package = pkgs.python311;
     venv = {
      enable = true;
      requirements = ./requirements.txt;
     };
  };

  enterShell = ''
  	echo "~~ ogrodje-observer @ $OGRODJE_OBSERVER_ENV ~~"
  '';
  
  enterTest = ''
    echo "Running tests"
  '';

}
