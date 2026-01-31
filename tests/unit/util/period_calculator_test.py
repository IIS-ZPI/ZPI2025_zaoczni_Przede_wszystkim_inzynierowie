from datetime import date

from app.util.period_calculator import PeriodCalculator, MAX_DAYS

def test_calculate_start_date_one_week():
    end = date(2024, 1, 8)
    start = PeriodCalculator.calculate_start_date(end, "1-week")
    assert start == date(2024, 1, 1)

def test_calculate_start_date_2_weeks():
    end = date(2024, 1, 15)
    start = PeriodCalculator.calculate_start_date(end, "2-weeks")
    assert start == date(2024, 1, 1)

def test_calculate_start_date_1_month_same_day():
    end = date(2024, 5, 15)
    start = PeriodCalculator.calculate_start_date(end, "1-month")
    assert start == date(2024, 4, 15)

def test_calculate_start_date_1_month_end_of_month():
    end = date(2024, 3, 31)
    start = PeriodCalculator.calculate_start_date(end, "1-month")
    assert start == date(2024, 2, 29)

def test_calculate_start_date_1_quarter():
    end = date(2024, 7, 31)
    start = PeriodCalculator.calculate_start_date(end, "1-quarter")
    assert start == date(2024, 4, 30)

def test_calculate_start_date_6_months():
    end = date(2024, 8, 31)
    start = PeriodCalculator.calculate_start_date(end, "6-months")
    assert start == date(2024, 2, 29)

def test_calculate_start_date_1_year_regular():
    end = date(2024, 6, 10)
    start = PeriodCalculator.calculate_start_date(end, "1-year")
    assert start == date(2023, 6, 10)

def test_calculate_start_date_1_year_feb_29():
    end = date(2024, 2, 29)
    start = PeriodCalculator.calculate_start_date(end, "1-year")
    assert start == date(2023, 2, 28)

def test_split_date_range_single_chunk():
    start = date(2024, 1, 1)
    end = date(2024, 3, 31)
    ranges = PeriodCalculator.split_date_range(start, end)
    assert ranges == [(start, end)]

def test_split_date_range_multiple_chunks():
    start = date(2024, 1, 1)
    end = date(2024, 7, 1)

    ranges = PeriodCalculator.split_date_range(start, end)

    for r_start, r_end in ranges:
        assert (r_end - r_start).days < MAX_DAYS

    assert ranges[0][0] == start
    assert ranges[-1][1] == end