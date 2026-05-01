from medbill_checker.services.parser import BillParser


def test_parser_extracts_line_items_and_total():
    text = """
    CBC Lab Test $120.00
    Room Charge x 2 $800.00
    Lipitor 20mg Qty: 30 $95.00
    Total Amount Due: $1,015.00
    """

    result = BillParser().parse(text)

    assert len(result.line_items) == 3
    assert result.parsed_total == 1015.00
    assert any(item.category.value == "medication" for item in result.line_items)
