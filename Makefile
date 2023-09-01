run_ci_locally:
	echo "If you don't have nix-shell installed, go to https://nixos.org/download.html"
	nix-shell -p act --run "act --secret-file env.secrets --env-file env.secrets -j black --insecure-secrets"
