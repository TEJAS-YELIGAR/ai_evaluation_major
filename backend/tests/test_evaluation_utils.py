from app.utils.evaluation_utils import build_module_results


def test_selects_higher_question_without_adding_alternatives():
    modules = build_module_results({1: 14, 2: 17})

    assert modules[0]["final_marks"] == 17
    assert modules[0]["selected_questions"] == [2]
    assert modules[0]["question_scores"] == [14, 17]


def test_unanswered_module_scores_zero():
    modules = build_module_results({})

    assert modules[0]["final_marks"] == 0


def test_equal_scores_retain_tie_score():
    modules = build_module_results({1: 12, 2: 12})

    assert modules[0]["final_marks"] == 12
    assert modules[0]["selected_questions"] == [1, 2]
    assert modules[0]["selection_status"] == "Tie"


def test_module_score_is_capped_at_twenty():
    modules = build_module_results({1: 25, 2: 24})

    assert modules[0]["final_marks"] == 20
    assert sum(module["final_marks"] for module in modules) <= 100