from higgs_voice_studio.parsing import parse_document, split_paragraphs, strip_leading_ordinal


def test_split_blank_lines():
    assert split_paragraphs("A\n\nB\n \nC") == ["A", "B", "C"]


def test_strip_number():
    number, text = strip_leading_ordinal("12. Xin chào thế giới")
    assert number == 12
    assert text == "Xin chào thế giới"


def test_filename_and_spoken_text():
    items = parse_document("1. Xin chào mọi người hôm nay rất vui\n\n2. Hello world this is a test")
    assert len(items) == 2
    assert items[0].spoken_text.startswith("Xin chào")
    assert items[0].filename == "001_Xin_chao_moi_nguoi_hom.wav"
    assert items[1].filename == "002_Hello_world_this_is_a.wav"
