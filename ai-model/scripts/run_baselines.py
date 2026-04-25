import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Callable, Any


API_URL = "http://127.0.0.1:8001/api/generate"


@dataclass
class Case:
    name: str
    payload: dict[str, Any]
    checker: Callable[[dict[str, Any]], tuple[bool, str]]


def post_json(url: str, payload: dict[str, Any], timeout: int = 120) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body)


def check_text_has_structure(resp: dict[str, Any]) -> tuple[bool, str]:
    text = resp.get("text_response") or ""
    if resp.get("error"):
        return False, f"error from API: {resp['error']}"
    has_sources = "SOURCES" in text
    has_answer = "ANSWER" in text
    has_conf = "CONFIDENCE" in text
    if has_sources and has_answer and has_conf:
        return True, "contains SOURCES/ANSWER/CONFIDENCE"
    return False, "missing one of SOURCES/ANSWER/CONFIDENCE"


def check_text_insufficient_data(resp: dict[str, Any]) -> tuple[bool, str]:
    text = (resp.get("text_response") or "").lower()
    if resp.get("error"):
        return False, f"error from API: {resp['error']}"
    markers = ["недостат", "insufficient", "не хватает", "нет данных"]
    if any(m in text for m in markers):
        return True, "insufficient-data signal found"
    return False, "no explicit insufficient-data signal found"


def check_text_conflict(resp: dict[str, Any]) -> tuple[bool, str]:
    text = (resp.get("text_response") or "").lower()
    if resp.get("error"):
        return False, f"error from API: {resp['error']}"
    has_conflict = any(m in text for m in ["conflict", "противореч", "расхожд"])
    has_sources = "sources" in text
    if has_conflict and has_sources:
        return True, "conflict and sources mentioned"
    return False, "conflict or sources are not explicit"


def check_chart_status_aggregation(resp: dict[str, Any]) -> tuple[bool, str]:
    if resp.get("error"):
        return False, f"error from API: {resp['error']}"
    chart = resp.get("chart_data")
    if not chart:
        return False, "chart_data is empty"

    labels = chart.get("labels") or []
    values = chart.get("values") or []
    if len(labels) != len(values):
        return False, "labels and values length mismatch"

    expected = {"Done": 2, "In Progress": 1}
    got = dict(zip(labels, values))
    if all(got.get(k) == v for k, v in expected.items()):
        return True, "status aggregation looks correct"
    return False, f"unexpected aggregation: {got}"


def check_chart_empty_ok(resp: dict[str, Any]) -> tuple[bool, str]:
    if resp.get("error"):
        return False, f"error from API: {resp['error']}"

    chart = resp.get("chart_data")
    if not chart:
        return False, "chart_data is empty"

    labels = chart.get("labels") or []
    values = chart.get("values") or []
    if len(labels) == 0 and len(values) == 0:
        return True, "empty chart is valid"
    if len(labels) == len(values):
        return True, "non-empty but structurally valid chart"
    return False, "invalid chart structure"


def build_cases() -> list[Case]:
    return [
        Case(
            name="T1: enough data",
            payload={
                "user_query": "Сколько задач в статусе Done?",
                "documents": [
                    "Task A - Done",
                    "Task B - In Progress",
                    "Task C - Done",
                ],
                "response_type": "text",
            },
            checker=check_text_has_structure,
        ),
        Case(
            name="T2: insufficient data",
            payload={
                "user_query": "Кто владелец проекта?",
                "documents": ["Project timeline: Q2 release"],
                "response_type": "text",
            },
            checker=check_text_insufficient_data,
        ),
        Case(
            name="T3: conflicting data",
            payload={
                "user_query": "Какой дедлайн у релиза?",
                "documents": [
                    "Release deadline: 2026-05-20",
                    "Release deadline: 2026-05-25",
                ],
                "response_type": "text",
            },
            checker=check_text_conflict,
        ),
        Case(
            name="C1: status aggregation",
            payload={
                "user_query": "Построй график по статусам задач",
                "documents": [
                    "Tasks: Task A (Done), Task B (Done), Task C (In Progress)"
                ],
                "response_type": "chart",
            },
            checker=check_chart_status_aggregation,
        ),
        Case(
            name="C2: empty chart fallback",
            payload={
                "user_query": "Сделай график по приоритетам",
                "documents": [],
                "response_type": "chart",
            },
            checker=check_chart_empty_ok,
        ),
    ]


def main() -> int:
    cases = build_cases()
    passed = 0

    print(f"Running {len(cases)} baseline cases against {API_URL}\n")

    for idx, case in enumerate(cases, start=1):
        print(f"[{idx}/{len(cases)}] {case.name}")
        try:
            response_json = post_json(API_URL, case.payload)
            ok, details = case.checker(response_json)
            status = "PASS" if ok else "FAIL"
            print(f"  {status}: {details}")
            print(f"  raw: {json.dumps(response_json, ensure_ascii=False)}")
            if ok:
                passed += 1
        except urllib.error.URLError as exc:
            print(f"  FAIL: cannot reach API - {exc}")
        except Exception as exc:
            print(f"  FAIL: unexpected error - {exc}")

        print()

    print(f"Summary: {passed}/{len(cases)} passed")
    return 0 if passed == len(cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())
