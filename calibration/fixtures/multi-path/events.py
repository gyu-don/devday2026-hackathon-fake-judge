from planner import make_plan


def on_task(event, documents, allowed_ids, seen):
    if event["id"] in seen:
        return {"status": "duplicate"}
    readable = [d for d in documents if d["id"] in allowed_ids]
    result = make_plan(readable)
    if result["status"] == "draft":
        seen.add(event["id"])
    return result
