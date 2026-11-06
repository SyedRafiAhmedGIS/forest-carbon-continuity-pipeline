# Forest Carbon Continuity Pipeline - Quick Commands
.PHONY: setup test run clean

# Hour 1: Setup the environment
setup:
	@echo "🚀 Setting up Conda environment..."
	conda env create -f environment.yaml
	@echo "✅ Setup complete! Run 'conda activate forest-carbon-continuity'"

# Hour 2: Run automated guardrails
test:
	@echo "🛡️ Running pytest guardrails..."
	pytest tests/ -v

# Run the Jupyter interface
run:
	@echo "🚀 Starting Jupyter Lab..."
	jupyter lab --ip=0.0.0.0 --allow-root --no-browser

# Clean up outputs and quarantine
clean:
	rm -rf quarantine/ outputs/ .ipynb_checkpoints/
	@echo "🧹 Workspace cleaned."
