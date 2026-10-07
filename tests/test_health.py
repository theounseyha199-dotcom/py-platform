from app.main import health


def test_health() -> None:
    assert health() == {"status": "success", "message": "Coffee Shop API is running"}
