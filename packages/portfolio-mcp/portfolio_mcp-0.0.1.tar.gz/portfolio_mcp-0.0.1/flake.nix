{
  description = "portfolio-mcp - Portfolio analysis MCP server powered by mcp-refcache";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
        };

        fhsEnv = pkgs.buildFHSEnv {
          name = "portfolio-mcp-dev-env";

          targetPkgs = pkgs':
            with pkgs'; [
              # Python and uv
              python312
              uv

              # System libraries (required for some dependencies)
              zlib
              stdenv.cc.cc.lib

              # Shells
              zsh
              bash

              # Linting & Formatting
              ruff
              pre-commit

              # Development tools
              git
              git-lfs
              curl
              wget
              jq
              tree
              httpie
            ];

          profile = ''
            echo "📊 portfolio-mcp Development Environment"
            echo "========================================="

            # Create and activate uv virtual environment if it doesn't exist
            if [ ! -d ".venv" ]; then
              echo "📦 Creating uv virtual environment..."
              uv venv --python python3.12 --prompt "portfolio-mcp"
            fi

            # Activate the virtual environment
            source .venv/bin/activate

            # Set a recognizable name for IDEs
            export VIRTUAL_ENV_PROMPT="portfolio-mcp"

            # Sync dependencies
            if [ -f "pyproject.toml" ]; then
              echo "🔄 Syncing dependencies..."
              uv sync --quiet
            else
              echo "⚠️  No pyproject.toml found. Run 'uv init' to create project."
            fi

            echo ""
            echo "✅ Python: $(python --version)"
            echo "✅ uv:     $(uv --version)"
            echo "✅ Virtual environment: activated (.venv)"
            echo "✅ PYTHONPATH: $PWD/app:$PWD"
          '';

          runScript = ''
            # Set shell for the environment
            SHELL=${pkgs.zsh}/bin/zsh

            # Set PYTHONPATH to project root for module imports
            export PYTHONPATH="$PWD/app:$PWD"
            export SSL_CERT_FILE="/etc/ssl/certs/ca-bundle.crt"

            echo ""
            echo "📊 portfolio-mcp Quick Reference:"
            echo ""
            echo "🔧 Development:"
            echo "  uv sync                    - Sync dependencies"
            echo "  uv run pytest              - Run tests"
            echo "  uv run ruff check .        - Lint code"
            echo "  uv run ruff format .       - Format code"
            echo "  uv lock --upgrade          - Update all dependencies"
            echo ""
            echo "📦 Package Management:"
            echo "  uv add <package>           - Add runtime dependency"
            echo "  uv add --dev <package>     - Add dev dependency"
            echo "  uv remove <package>        - Remove dependency"
            echo ""
            echo "🚀 Run Server:"
            echo "  uv run portfolio-mcp           - Run MCP server (stdio)"
            echo "  uv run portfolio-mcp --transport sse --port 8000"
            echo ""
            echo "📊 Features:"
            echo "  - Portfolio creation (Yahoo Finance, CoinGecko, Synthetic)"
            echo "  - Analysis (returns, volatility, Sharpe, Sortino, VaR)"
            echo "  - Optimization (Efficient Frontier, Monte Carlo)"
            echo "  - Reference-based caching via mcp-refcache"
            echo ""
            echo "🚀 Ready to build!"
            echo ""

            # Start zsh shell
            exec ${pkgs.zsh}/bin/zsh
          '';
        };
      in {
        devShells.default = pkgs.mkShell {
          shellHook = ''
            exec ${fhsEnv}/bin/portfolio-mcp-dev-env
          '';
        };

        packages.default = pkgs.python312;
      }
    );
}
