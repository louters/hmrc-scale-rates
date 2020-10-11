import unittest
import json
import datetime
from helpers import compute_rates


class TestComputeRatesMorning(unittest.TestCase):
    def setUp(self):
        with open("rates", "r") as f:
            self.rates = json.load(f)
        self.rates = self.rates["France"]["Paris"]
        self.dt_in = datetime.datetime(2020, 5, 25, 9, 17)


    def test_sameday(self):
        # Test for same day less than 5h
        dt_out = self.dt_in + datetime.timedelta(hours=4)
        self.assertEqual(0, compute_rates(self.rates, self.dt_in, dt_out)[0])
        # Test for same day over 5h OK
        dt_out = self.dt_in + datetime.timedelta(hours=6)
        self.assertEqual(40, compute_rates(self.rates, self.dt_in, dt_out)[0])
        # Test for same day over 10h OK
        dt_out = self.dt_in + datetime.timedelta(hours=11)
        self.assertEqual(86.5, compute_rates(self.rates, self.dt_in, dt_out)[0])


    def test_nextday(self):
        # Test for next day less than 24h
        dt_out = self.dt_in + datetime.timedelta(hours=23)
        self.assertEqual(286, compute_rates(self.rates, self.dt_in, dt_out)[0])

        # Test for next day more than 24h, less than 5 hours
        dt_out = self.dt_in + datetime.timedelta(hours=25)
        self.assertEqual(316.5, compute_rates(self.rates, self.dt_in, dt_out)[0])

        # Test for next day more than 24h, over 5 hours, less than 10 hours
        dt_out = self.dt_in + datetime.timedelta(hours=30)
        self.assertEqual(356.5, compute_rates(self.rates, self.dt_in, dt_out)[0])

        # Test for next day more than 24h, over 10 hours
        dt_out = self.dt_in + datetime.timedelta(hours=35)
        self.assertEqual(403, compute_rates(self.rates, self.dt_in, dt_out)[0])


    def test_multidays(self):
        # Test for 3x24h, less than 5 hours
        dt_out = self.dt_in + datetime.timedelta(days=3, hours=1)
        self.assertEqual(949.5, compute_rates(self.rates, self.dt_in, dt_out)[0])

        # Test for 3x24h, over 5 hours, less than 10 hours
        dt_out = self.dt_in + datetime.timedelta(days=3, hours=6)
        self.assertEqual(989.5, compute_rates(self.rates, self.dt_in, dt_out)[0])

        # Test for 3x24h, over 10 hours
        dt_out = self.dt_in + datetime.timedelta(days=3, hours=11)
        self.assertEqual(1036, compute_rates(self.rates, self.dt_in, dt_out)[0])


class TestComputeRatesEvening(unittest.TestCase):
    def setUp(self):
        with open("rates", "r") as f:
            self.rates = json.load(f)
        self.rates = self.rates["France"]["Paris"]
        self.dt_in = datetime.datetime(2020, 5, 25, 21, 17)


    def test_nextday(self):
        # Test for next day less than 24h
        dt_out = self.dt_in + datetime.timedelta(hours=4)
        self.assertEqual(199.5, compute_rates(self.rates, self.dt_in, dt_out)[0])

        # Test for next day less, over than 5 hours, less than 10 hours
        dt_out = self.dt_in + datetime.timedelta(hours=6)
        self.assertEqual(239.5, compute_rates(self.rates, self.dt_in, dt_out)[0])

        # Test for next day over 10 hours
        dt_out = self.dt_in + datetime.timedelta(hours=11)
        self.assertEqual(286, compute_rates(self.rates, self.dt_in, dt_out)[0])

        # Test for next day than 24h
        dt_out = self.dt_in + datetime.timedelta(hours=25)
        self.assertEqual(316.5, compute_rates(self.rates, self.dt_in, dt_out)[0])


    def test_multinights(self):
        # Test for 2x24h, less than 5 hours
        dt_out = self.dt_in + datetime.timedelta(days=2, hours=1)
        self.assertEqual(633, compute_rates(self.rates, self.dt_in, dt_out)[0])

        # Test for 2x24h, over 5 hours, less than 10 hours + room rate
        dt_out = self.dt_in + datetime.timedelta(days=2, hours=6)
        self.assertEqual(872.5, compute_rates(self.rates, self.dt_in, dt_out)[0])

        # Test for 2x24h, over 10 hours
        dt_out = self.dt_in + datetime.timedelta(days=2, hours=11)
        self.assertEqual(919, compute_rates(self.rates, self.dt_in, dt_out)[0])


if __name__ == "__main__":
    unittest.main()