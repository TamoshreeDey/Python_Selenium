# E-Commerce Web Automation Framework

An automated end-to-end testing framework for an E-Commerce web application built using **Python**, **Selenium WebDriver**, and **pytest**.

## Project Structure
```text
Python_Selenium/
│
├── .gitignore
├── README.md
└── ecommerce_auto/
    ├── config.py           # Configuration paths and dynamic setups
    ├── data.json           # Externalized test data
    ├── test_runner.py      # Page Object Model (POM) implementation & tests
    ├── report.html         # Generated execution report (git-ignored)
    └── screenshots/        # Captured execution screenshots (git-ignored)