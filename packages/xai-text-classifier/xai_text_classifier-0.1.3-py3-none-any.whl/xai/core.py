from dataclasses import dataclass
import joblib
import pandas as pd
from typing import Any, Dict, List, Optional, Union
import shap
from pathlib import Path
import os

from .utils import get_features_from_text

# Get the directory where this module is located
MODULE_DIR = Path(__file__).parent

@dataclass
class XAI:
    xgb_model = joblib.load(MODULE_DIR / 'XGB_model.joblib')
    rf_model = joblib.load(MODULE_DIR / 'Random_Forest_model.joblib')
    data = pd.read_csv(MODULE_DIR / 'coling.csv')

    def shap_explainer(self,text:str) -> Dict[str, Any]:
        """
        Return SHAP explanations for ALL features in dictionary form.

        Parameters:
        - text: input text to explain whether AI-generated or Human-written

        Returns:
        - dict of feature → explanation details
        """

        # === SHAP Explainer ===

        sample_features = get_features_from_text(text)
        prediction = self.xgb_model.predict(sample_features)[0]
        explainer = shap.TreeExplainer(self.xgb_model)

        # shap_values = explainer(self.data)   # background
        sample_shap = explainer(sample_features)  # current sample

        # Full model-based feature importance
        importance_df = (
            pd.DataFrame({
                "Feature": self.xgb_model.get_booster().feature_names,
                "Importance": self.xgb_model.feature_importances_
            })
            .sort_values("Importance", ascending=False)
            .reset_index(drop=True)
        )

        # Build dictionary of explanations
        explanations = {}

        for rank, row in importance_df.iterrows():
            feat = row["Feature"]
            shap_val = sample_shap.values[0][self.data.columns.get_loc(feat)]
            direction = "AI" if shap_val > 0 else "Human"
            magnitude = float(abs(shap_val))
            value = float(sample_features[feat].iloc[0])

            explanations[feat] = {
                "Sample_Value": value,
                "SHAP_Value": float(round(shap_val, 6)),
                "Direction": direction,
                "Contribution_Strength": magnitude,
                "Feature_Importance_Rank": int(rank + 1),
                "Model_Importance": float(row["Importance"])
            }
        if prediction == 1:
            explanations["prediction"] = "AI-generated"
        else:
            explanations["prediction"] = "Human-written"
        return explanations


