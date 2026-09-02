import pytest

from core.stemmer import (
    porter_transform,
    step_1a,
    step_1b,
    step_1c,
    step_2,
    step_3,
    step_4,
    step_5a,
    step_5b,
    m_value,
    contains_vowel,
    star_o,
    stem_tokens
)

class TestCustomTests:
    """
    Tests the entire algorithm as a whole or individual steps
    """
    def test_words(self):
        assert porter_transform("feed") == "feed"
        assert porter_transform("runner") == "runner"
        assert porter_transform("running") == "run"
        
    def test_steps(self):
        w = "caress"
        for f in [step_1a, step_1b, step_1c, step_2, step_3, step_4, step_5a, step_5b]:
            w = f(w)
            assert w == "caress"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])