import algokit_utils
import pytest
from algokit_utils import get_localnet_default_account
from algokit_utils.config import config
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient

from smart_contracts.artifacts.contract.contract_client import ContractClient

@pytest.fixture(scope="session")
def contract_client(algod_client: AlgodClient, indexer_client: IndexerClient) -> ContractClient:
    config = config.get("contract")
    app_spec = config.app_spec

    client = ContractClient(
        algod_client,
        creator=get_localnet_default_account(algod_client),
        indexer_client=indexer_client,
    )

    client.deploy(
        on_schema_break=algokit_utils.OnSchemaBreak.ReplaceApp,
        on_update=algokit_utils.OnUpdate.UpdateApp,
        allow_delete=True,
        allow_update=True,
    )

    return client

def test_access_rights(contract_client: ContractClient):
    # Thêm tài nguyên mới
    resource_id = "resource1"
    resource_data = "Sensitive data"
    result = contract_client.add_resource(resource_id=resource_id, resource_data=resource_data)
    assert "Đã thêm tài nguyên thành công" in result.return_value

    # Thiết lập quyền sở hữu
    owner_address = contract_client.app_client.sender.address
    result = contract_client.set_resource_owner(resource_id=resource_id, owner_address=owner_address)
    assert f"Đã thiết lập quyền sở hữu cho tài nguyên {resource_id}" in result.return_value

    # Thiết lập quyền truy cập cho người dùng khác
    user_address = "USER_ADDRESS"
    rights = "read"
    result = contract_client.set_access_rights(resource_id=resource_id, user_address=user_address, rights=rights)
    assert f"Đã thiết lập quyền truy cập {rights} cho người dùng {user_address}" in result.return_value

    # Kiểm tra quyền truy cập
    result = contract_client.check_access_rights(resource_id=resource_id, user_address=user_address, action="read")
    assert f"Người dùng {user_address} có quyền read đối với tài nguyên {resource_id}" in result.return_value

    result = contract_client.check_access_rights(resource_id=resource_id, user_address=user_address, action="write")
    assert f"Người dùng {user_address} không có quyền write đối với tài nguyên {resource_id}" in result.return_value

    # Kiểm tra quyền của chủ sở hữu
    result = contract_client.check_access_rights(resource_id=resource_id, user_address=owner_address, action="write")
    assert f"Người dùng {owner_address} là chủ sở hữu của tài nguyên {resource_id}" in result.return_value

    # Thử truy cập tài nguyên
    result = contract_client.access_resource(resource_id=resource_id, user_token="VALID_TOKEN")
    assert result.return_value == resource_data

    # Thử truy cập với token không hợp lệ
    result = contract_client.access_resource(resource_id=resource_id, user_token="INVALID_TOKEN")
    assert "Không có quyền truy cập" in result.return_value

    # Kiểm tra hệ thống token
    
    # Mua token
    result = contract_client.buy_tokens(amount=10)
    assert "Đã mua thành công 10 token" in result.return_value
    
    # Kiểm tra số dư token
    balance = contract_client.get_token_balance()
    assert balance.return_value == 10
    
    # Chuyển token cho người dùng khác
    recipient = "RECIPIENT_ADDRESS"
    result = contract_client.transfer_tokens(recipient=recipient, amount=5)
    assert "Đã chuyển 5 token cho RECIPIENT_ADDRESS" in result.return_value
    
    # Kiểm tra lại số dư sau khi chuyển
    balance = contract_client.get_token_balance()
    assert balance.return_value == 5
    
    # Thử truy cập tài nguyên bằng token
    result = contract_client.access_resource(resource_id=resource_id, token_amount=2)
    assert f"Đã truy cập tài nguyên {resource_id}" in result.return_value
    
    # Kiểm tra số dư sau khi truy cập
    balance = contract_client.get_token_balance()
    assert balance.return_value == 3
    
    # Thử truy cập với số token không đủ
    result = contract_client.access_resource(resource_id=resource_id, token_amount=5)
    assert "Không đủ token để truy cập tài nguyên" in result.return_value

    # Kiểm tra tính năng thêm tài liệu
    doc_id = "DOC001"
    title = "Giới thiệu về Blockchain"
    author = "Satoshi Nakamoto"
    year = 2008
    field = "Công nghệ blockchain"
    content = "Blockchain là một công nghệ sổ cái phân tán..."
    
    result = contract_client.add_document(doc_id=doc_id, title=title, author=author, year=year, field=field, content=content)
    assert f"Đã thêm tài liệu {doc_id} thành công" in result.return_value
    
    # Thêm thêm một số tài liệu khác để kiểm tra tìm kiếm
    contract_client.add_document(doc_id="DOC002", title="Ethereum và Smart Contracts", author="Vitalik Buterin", year=2015, field="Công nghệ blockchain", content="Ethereum là một nền tảng blockchain...")
    contract_client.add_document(doc_id="DOC003", title="Giới thiệu về Machine Learning", author="Andrew Ng", year=2018, field="Trí tuệ nhân tạo", content="Machine Learning là một lĩnh vực của AI...")
    
    # Kiểm tra tìm kiếm theo lĩnh vực
    result = contract_client.search_documents(field="Công nghệ blockchain")
    assert "DOC001" in result.return_value
    assert "DOC002" in result.return_value
    assert "DOC003" not in result.return_value
    
    # Kiểm tra tìm kiếm theo tác giả
    result = contract_client.search_documents(author="Satoshi Nakamoto")
    assert "DOC001" in result.return_value
    assert "DOC002" not in result.return_value
    
    # Kiểm tra tìm kiếm theo năm
    result = contract_client.search_documents(year=2015)
    assert "DOC002" in result.return_value
    assert "DOC001" not in result.return_value
    
    # Kiểm tra tìm kiếm kết hợp
    result = contract_client.search_documents(field="Công nghệ blockchain", year=2008)
    assert "DOC001" in result.return_value
    assert "DOC002" not in result.return_value
    
    # Kiểm tra trường hợp không tìm thấy kết quả
    result = contract_client.search_documents(author="John Doe")
    assert "Không tìm thấy tài liệu phù hợp" in result.return_value
    
    # Kiểm tra lấy nội dung tài liệu
    result = contract_client.get_document_content(doc_id="DOC001")
    assert "Blockchain là một công nghệ sổ cái phân tán..." in result.return_value
    
    # Kiểm tra lấy nội dung tài liệu không tồn tại
    result = contract_client.get_document_content(doc_id="DOC999")
    assert "Tài liệu không tồn tại" in result.return_value



