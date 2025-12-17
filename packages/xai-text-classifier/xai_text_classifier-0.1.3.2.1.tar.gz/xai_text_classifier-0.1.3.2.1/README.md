# XAI Text Classifier

A library to explain whether text is AI-generated or human-written using SHAP (SHapley Additive exPlanations).

## Features

- **AI vs Human Text Classification**: Distinguish between AI-generated and human-written text
- **Explainability**: Uses SHAP to provide detailed feature importance explanations
- **Multiple Models**: Includes XGBoost and Random Forest models for robust predictions
- **Comprehensive Feature Analysis**: Analyzes 40+ linguistic features including:
  - Readability metrics
  - Sentiment analysis
  - Syntactic complexity
  - Stylistic patterns
  - And more

## Installation

```bash
pip install xai-text-classifier
```

Or install from source:

```bash
git clone <repository-url>
cd xai-text-classifier
pip install -e .
```

## Usage

```python
from xai import shap_explainer

# Analyze text
text = "Your text here..."
result = shap_explainer(text)

# Returns:
# {
#     "prediction": 0 or 1,  # 0 = Human, 1 = AI
#     "features": {
#         "feature_name": {
#             "value": feature_value,
#             "shap_value": shap_contribution,
#             "importance": relative_importance
#         },
#         ...
#     }
# }
```

## Requirements

- Python >= 3.8
- joblib
- shap
- xgboost
- spacy
- language-tool-python
- textblob
- pandas
- numpy
- scikit-learn
- nltk
- textstat
- matplotlib
- scipy

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this library in your research, please cite:

```bibtex
@software{xai_text_classifier,
  title={XAI Text Classifier},
  year={2025},
  url={<repository-url>}
}
```
