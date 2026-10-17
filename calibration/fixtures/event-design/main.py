def plan(event, seen):
    if event["id"] in seen:
        return None
    seen.add(event["id"])
    return {"status": "draft", "steps": ["資料確認", "担当者レビュー"]}

if __name__ == "__main__":
    print(plan({"id": "demo-1"}, set()))
