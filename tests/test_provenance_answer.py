from app.agents.provenance import (
    FinalAnswer,
    AnswerCitation,
    SourceCitation,
    render_answer,
)


def test_render_answer_with_citation():

    result = FinalAnswer(
        answer=(
            "Revenue was ₹17,206.06 million."
        ),
        citations=[
            AnswerCitation(
                claim=(
                    "Revenue was ₹17,206.06 million."
                ),
                citation=SourceCitation(
                    company="CULT.FIT LIMITED",
                    document_type="DRHP",
                    source="SEBI",
                    page_number=469,
                ),
            )
        ],
    )

    output = render_answer(
        result
    )

    assert (
        "₹17,206.06 million"
        in output
    )

    assert (
        "CULT.FIT LIMITED"
        in output
    )

    assert (
        "p. 469"
        in output
    )