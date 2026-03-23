"""Tests for input validation helpers."""

import pytest

from pydbsec._validation import validate_date, validate_price, validate_quantity, validate_stock_code


class TestValidateStockCode:
    def test_valid(self):
        validate_stock_code("005930")
        validate_stock_code("AAPL")

    def test_empty_string(self):
        with pytest.raises(ValueError, match="stock_code must be a non-empty string"):
            validate_stock_code("")

    def test_whitespace_only(self):
        with pytest.raises(ValueError, match="stock_code must be a non-empty string"):
            validate_stock_code("   ")

    def test_not_a_string(self):
        with pytest.raises(ValueError, match="stock_code must be a non-empty string"):
            validate_stock_code(123)  # type: ignore[arg-type]

    def test_custom_label(self):
        with pytest.raises(ValueError, match="code must be a non-empty string"):
            validate_stock_code("", label="code")


class TestValidateQuantity:
    def test_valid(self):
        validate_quantity(1)
        validate_quantity(100)

    def test_zero(self):
        with pytest.raises(ValueError, match="quantity must be a positive integer"):
            validate_quantity(0)

    def test_negative(self):
        with pytest.raises(ValueError, match="quantity must be a positive integer"):
            validate_quantity(-5)

    def test_float(self):
        with pytest.raises(ValueError, match="quantity must be a positive integer"):
            validate_quantity(1.5)  # type: ignore[arg-type]


class TestValidatePrice:
    def test_valid(self):
        validate_price(0)
        validate_price(100.5)
        validate_price(0.0)

    def test_negative(self):
        with pytest.raises(ValueError, match="price must be a non-negative number"):
            validate_price(-1)

    def test_not_a_number(self):
        with pytest.raises(ValueError, match="price must be a non-negative number"):
            validate_price("100")  # type: ignore[arg-type]


class TestValidateDate:
    def test_valid(self):
        validate_date("20260101")
        validate_date("20251231")

    def test_empty_not_allowed(self):
        with pytest.raises(ValueError, match="date must be in YYYYMMDD format"):
            validate_date("")

    def test_empty_allowed(self):
        validate_date("", allow_empty=True)

    def test_wrong_format(self):
        with pytest.raises(ValueError, match="date must be in YYYYMMDD format"):
            validate_date("2026-01-01")

    def test_too_short(self):
        with pytest.raises(ValueError, match="date must be in YYYYMMDD format"):
            validate_date("202601")

    def test_custom_label(self):
        with pytest.raises(ValueError, match="start_date must be in YYYYMMDD format"):
            validate_date("bad", label="start_date")

    def test_not_a_string(self):
        with pytest.raises(ValueError, match="date must be in YYYYMMDD format"):
            validate_date(20260101)  # type: ignore[arg-type]
