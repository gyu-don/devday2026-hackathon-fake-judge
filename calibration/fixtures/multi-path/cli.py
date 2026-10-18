from planner import make_plan


def main(documents):
    if not documents:
        return {"status": "needs_input", "message": "資料を指定して再入力してください"}
    return make_plan(documents)
