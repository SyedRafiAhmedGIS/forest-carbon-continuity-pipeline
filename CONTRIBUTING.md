# 🤝 Contributing to Forest Carbon Continuity Pipeline

This repository is built on the philosophy: *"If I leave tomorrow, what survives me?"*
We welcome contributions that improve reproducibility, accuracy, or scalability.

## 🗓️ Week 1 Onboarding Task: Prove the System Accepts Change
To verify your handover setup, please complete the following Pull Request (PR):
1. **Fork** this repository.
2. **Clone** your fork and create a new branch: `git checkout -b feat/update-threshold`.
3. **Make a Change**: Open `configs/ireland_config.yaml` and change `nfi_threshold_dbh_cm: 10.0` to `12.0`.
4. **Run Guardrails**: Execute `pytest tests/` to ensure no core logic broke.
5. **Open a PR**: Submit your changes to the `main` branch. The automated CI/CD pipeline will verify your code.

## 🛡️ Automated Guardrails
Every PR automatically triggers:
- **Unit Tests:** Checks Python module imports and logic.
- **Integration Tests:** Ensures the pipeline engine loads correctly.
- **Linting:** Checks for PEP8 compliance.

*If any gate fails, the build is rejected automatically. No human review needed for trivial breakages.*
