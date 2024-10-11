from collections.abc import Iterator

import pytest
from algopy_testing import AlgopyTestContext, algopy_testing_context

from smart_contracts.contract.contract import Contract


@pytest.fixture(scope="module")
def contract(algopy_testing_context: AlgopyTestContext) -> Iterator[Contract]:
    contract = Contract()
    algopy_testing_context.create_app(contract)
    yield contract


def test_data_integrity(contract: Contract):
    # Dữ liệu ban đầu
    original_data = "Đây là dữ liệu gốc cần bảo vệ"
    
    # Lưu trữ hash của dữ liệu
    result = contract.store_data_hash(original_data)
    assert "Đã lưu hash của dữ liệu:" in result
    
    # Kiểm tra tính toàn vẹn của dữ liệu gốc
    integrity_check = contract.verify_data_integrity(original_data)
    assert integrity_check == "Dữ liệu không bị thay đổi và toàn vẹn"
    
    # Thử thay đổi dữ liệu
    modified_data = "Đây là dữ liệu đã bị thay đổi"
    integrity_check_modified = contract.verify_data_integrity(modified_data)
    assert integrity_check_modified == "Không tìm thấy hash của dữ liệu trên blockchain"
    
    # Kiểm tra lại dữ liệu gốc
    integrity_check_original = contract.verify_data_integrity(original_data)
    assert integrity_check_original == "Dữ liệu không bị thay đổi và toàn vẹn"

