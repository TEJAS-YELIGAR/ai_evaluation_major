MODULE_QUESTIONS = ((1, 2), (3, 4), (5, 6), (7, 8), (9, 10))


def build_module_results(question_totals: dict[int, float], module_max: float = 20.0):
    modules = []

    for module_no, question_nos in enumerate(MODULE_QUESTIONS, start=1):
        scores = [float(question_totals.get(question_no, 0)) for question_no in question_nos]
        highest_score = max(scores)
        selected_questions = [
            question_no
            for question_no, score in zip(question_nos, scores)
            if score == highest_score
        ]
        modules.append({
            "module_no": module_no,
            "question_nos": list(question_nos),
            "question_scores": scores,
            "selected_questions": selected_questions,
            "selection_status": "Tie" if len(selected_questions) == 2 else "Selected",
            "final_marks": min(module_max, highest_score),
            "max_marks": module_max,
        })

    return modules