from .core import XAI

# Initialize the explainer instance
_explainer = XAI()

# Export the shap_explainer function
def shap_explainer(text: str):
    """
    Explain whether text is AI-generated or human-written.
    
    Parameters:
    - text: input text to explain
    
    Returns:
    - dict of feature → explanation details with prediction
    """
    return _explainer.shap_explainer(text)

__all__ = ['shap_explainer']
