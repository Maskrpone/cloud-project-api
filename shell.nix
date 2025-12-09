{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
	buildInputs = with pkgs; [
		(python3.withPackages(ps: with ps; [
													python-lsp-server
													ipython
													jupyter
													pip
													sqlalchemy
													pyodbc
													fastapi
													fastapi-cli
													openpyxl
													pandas
													typing
													sqlmodel
		]))

			# Driver for mssql
			unixODBCDrivers.msodbcsql18		
			unixODBCDrivers.msodbcsql17
			unixODBC

			# pytest
			pyright
			ruff

			docker-language-server
			docker-compose-language-service

			terraform-ls
			terraform
	];

	shellHook = ''
		echo "Environment up !"
		if [ -f .env ]; then
      set -a
      source .env
      set +a
    fi
		exec zsh
		'';
}
