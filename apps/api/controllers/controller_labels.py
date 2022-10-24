from __future__ import annotations

from typing import Dict, List

from models.label import Label


class ControllerLabels:
    @staticmethod
    def labels_to_dict(labels: List[Label]) -> List[Dict]:
        result = []

        for label in labels:
            result.append({
                "label_name": label.label_name,
            })

        return result
