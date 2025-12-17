{
  description = "FinQuant - A program for financial portfolio management, analysis and optimisation";

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
          name = "finquant-dev-env";

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
            ];

          profile = ''
            echo "📈 FinQuant Development Environment"
            echo "===================================="

            # Create and activate uv virtual environment if it doesn't exist
            if [ ! -d ".venv" ]; then
              echo "📦 Creating uv virtual environment..."
              uv venv --python python3.12 --prompt "finquant"
            fi

            # Activate the virtual environment
            source .venv/bin/activate

            # Set a recognizable name for IDEs
            export VIRTUAL_ENV_PROMPT="finquant"

            # Install in editable mode if setup.py exists
            if [ -f "setup.py" ]; then
              echo "🔄 Installing FinQuant in editable mode..."
              uv pip install -e ".[dev,test]" --quiet 2>/dev/null || uv pip install -e . --quiet
            fi

            echo ""
            echo "✅ Python: $(python --version)"
            echo "✅ uv:     $(uv --version)"
            echo "✅ Virtual environment: activated (.venv)"
          '';

          runScript = ''
            # Set shell for the environment
            SHELL=${pkgs.zsh}/bin/zsh

            # Set PYTHONPATH to project root for module imports
            export PYTHONPATH="$PWD:$PYTHONPATH"
            export SSL_CERT_FILE="/etc/ssl/certs/ca-bundle.crt"

            echo ""
            echo "📈 FinQuant Quick Reference:"
            echo ""
            echo "🔧 Development:"
            echo "  uv pip install -e .        - Install in editable mode"
            echo "  uv pip install -e .[dev]   - Install with dev dependencies"
            echo "  uv run pytest              - Run tests"
            echo "  uv run ruff check .        - Lint code"
            echo "  uv run ruff format .       - Format code"
            echo ""
            echo "📦 Building & Publishing:"
            echo "  uv build                   - Build wheel and sdist"
            echo "  uv publish                 - Publish to PyPI"
            echo ""
            echo "📊 Features:"
            echo "  - Portfolio management and analysis"
            echo "  - Efficient Frontier optimization"
            echo "  - Monte Carlo simulation"
            echo "  - Moving averages and returns analysis"
            echo ""
            echo "🚀 Ready to develop!"
            echo ""

            # Start zsh shell
            exec ${pkgs.zsh}/bin/zsh
          '';
        };
      in {
        devShells.default = pkgs.mkShell {
          shellHook = ''
            exec ${fhsEnv}/bin/finquant-dev-env
          '';
        };

        packages.default = pkgs.python312;
      }
    );
}
