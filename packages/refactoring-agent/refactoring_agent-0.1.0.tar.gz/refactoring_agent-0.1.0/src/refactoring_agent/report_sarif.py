import json
import os
from typing import List, Dict
from . import __version__

def generate_sarif_report(issues_map: Dict[str, List[Dict]], output_path: str):
    """
    Генерирует отчет в формате SARIF (стандарт для GitHub Security).
    """
    
    # 1. Базовая структура SARIF
    sarif_log = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Refactoring Agent",
                        "version": __version__,
                        "informationUri": "https://github.com/StasLee1982/refactoring-agent",
                        "rules": []
                    }
                },
                "results": []
            }
        ]
    }

    run = sarif_log["runs"][0]
    rules_check = set()

    # 2. Проходим по всем найденным проблемам
    for file_path, issues in issues_map.items():
        # Приводим путь к относительному виду для CI/CD
        try:
            rel_path = os.path.relpath(file_path, os.getcwd())
        except ValueError:
            rel_path = file_path

        for issue in issues:
            rule_id = issue.get("rule_id", "unknown")
            message = issue.get("message", "Issue detected")
            line = issue.get("line", 1)
            # Защита от line=0 или None
            if not isinstance(line, int) or line < 1:
                line = 1
            
            severity = issue.get("severity", "warning")
            
            # Добавляем правило в список определений, если его там нет
            if rule_id not in rules_check:
                rules_check.add(rule_id)
                run["tool"]["driver"]["rules"].append({
                    "id": rule_id,
                    "shortDescription": {
                        "text": f"Rule: {rule_id}"
                    },
                    "helpUri": "https://github.com/StasLee1982/refactoring-agent"
                })

            # Формируем результат (Result)
            sarif_result = {
                "ruleId": rule_id,
                "level": "error" if severity in ("critical", "major") else "warning",
                "message": {
                    "text": message
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": rel_path
                            },
                            "region": {
                                "startLine": line
                            }
                        }
                    }
                ]
            }
            run["results"].append(sarif_result)

    # 3. Записываем файл
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(sarif_log, f, indent=2)
        print(f"[REPORT] SARIF report saved to: {output_path}")
    except Exception as e:
        print(f"[ERROR] Failed to save SARIF report: {e}")
