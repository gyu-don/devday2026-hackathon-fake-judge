def make_plan(documents):
    if not documents:
        return {"status": "needs_input", "message": "権限内の資料を追加してください"}
    return {
        "status": "draft",
        "steps": ["資料を確認", "担当者がレビュー"],
        "sources": [d["id"] for d in documents],
        "requires_review": True,
    }
