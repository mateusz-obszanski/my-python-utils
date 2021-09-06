from text.transform.case_conversion import converted_case, Case


class TestConvertedCase:
    AnswerMapping = dict[str, str]
    ToCaseMapping = dict[Case, AnswerMapping]

    def test_empty(self):
        assert converted_case("", "camel", "kebab") == ""

    def test_from_camel(self):
        case_answer_mapping: TestConvertedCase.ToCaseMapping = {
            "camel": {
                "loremIpsum": "loremIpsum",
                "LoremIpsum": "LoremIpsum",
                "$!@#%!@$@!#@loremIpsum": "$!@#%!@$@!#@loremIpsum",
                "&^$&$2131(*&": "&^$&$2131(*&",
            },
            "kebab": {
                "loremIpsum": "lorem-ipsum",
                "LoremIpsum": "lorem-ipsum",
                "$!@#%!@$@!#@loremIpsum": "$!@#%!@$@!#@lorem-ipsum",
                "&^$&$2131(*&": "&^$&$2131(*&",
            },
        }
        for case, answer_mapping in case_answer_mapping.items():
            for arg, answer in answer_mapping.items():
                assert converted_case(arg, "camel", case) == answer

    def test_from_kebab(self):
        case_answer_mapping: TestConvertedCase.ToCaseMapping = {
            "camel": {
                "lorem-ipsum": "loremIpsum",
                "$!@#%!@$@!#@lorem-ipsum": "$!@#%!@$@!#@loremIpsum",
                "&^$&$2131(*&": "&^$&$2131(*&",
            },
            "kebab": {
                "lorem-ipsum": "lorem-ipsum",
                "$!@#%!@$@!#@lorem-ipsum": "$!@#%!@$@!#@lorem-ipsum",
                "&^$&$2131(*&": "&^$&$2131(*&",
            },
            "snake": {
                "lorem-ipsum": "lorem_ipsum",
                "$!@#%!@$@!#@lorem-ipsum": "$!@#%!@$@!#@lorem_ipsum",
                "&^$&$2131(*&": "&^$&$2131(*&",
            },
        }
        for case, answer_mapping in case_answer_mapping.items():
            for arg, answer in answer_mapping.items():
                assert converted_case(arg, "kebab", case) == answer

    def test_from_custom_sep(self):
        assert converted_case("lorem-ipsum", "-", None) == "loremIpsum"
        assert converted_case("lorem-ipsum", "-", "camel") == "loremIpsum"
        assert converted_case("lorem-ipsum", "kebab", None) == "loremIpsum"
