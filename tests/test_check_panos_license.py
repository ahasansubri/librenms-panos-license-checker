#!/usr/bin/env python3

import importlib.machinery
import importlib.util
import sys
import unittest
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1] / "plugins" / "check_panos_license"
loader = importlib.machinery.SourceFileLoader("check_panos_license", str(PLUGIN))
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
sys.modules[loader.name] = module
loader.exec_module(module)


def expiry(days_from_today: int) -> str:
    return (date.today() + timedelta(days=days_from_today)).strftime("%B %d, %Y")


class PanosLicenceCheckerTests(unittest.TestCase):
    def test_cli_style_result(self):
        result = ET.fromstring(
            "<result>License entry:\n"
            "Feature: Advanced Threat Prevention\n"
            "Serial: REDACTED\n"
            "Authcode: REDACTED\n"
            f"Expires: {expiry(120)}\n"
            "Expired?: no\n</result>"
        )
        licences, perpetual = module.parse_api_result(result, [])
        self.assertEqual(len(licences), 1)
        self.assertEqual(licences[0].feature, "Advanced Threat Prevention")
        self.assertEqual(perpetual, 0)
        status, message = module.evaluate(licences, 60, 30)
        self.assertEqual(status, module.OK)
        self.assertNotIn("Serial", message)
        self.assertNotIn("Authcode", message)

    def test_structured_xml_warning(self):
        result = ET.fromstring(
            "<result><licenses><entry>"
            "<feature>Premium Support</feature>"
            f"<expires>{expiry(45)}</expires>"
            "<expired>no</expired>"
            "</entry></licenses></result>"
        )
        licences, _ = module.parse_api_result(result, [])
        status, _ = module.evaluate(licences, 60, 30)
        self.assertEqual(status, module.WARNING)

    def test_critical_expiry(self):
        licences = [module.Licence("Threat Prevention", date.today() - timedelta(days=1), True)]
        status, message = module.evaluate(licences, 60, 30)
        self.assertEqual(status, module.CRITICAL)
        self.assertIn("expired 1 day(s) ago", message)

    def test_perpetual_and_ignore(self):
        self.assertIsNone(module.parse_expiry("Never expires"))
        self.assertTrue(module.ignored("Software warranty", ["Software*"]))

    def test_extracts_successful_result(self):
        result = module.extract_result('<response status="success"><result>ok</result></response>')
        self.assertEqual(result.text, "ok")

    def test_rejects_failed_api_response(self):
        with self.assertRaises(RuntimeError):
            module.extract_result('<response status="error"><msg>denied</msg></response>')

    def test_threshold_order(self):
        licences = [module.Licence("Example", date.today() + timedelta(days=10), False)]
        status, _ = module.evaluate(licences, 60, 30)
        self.assertEqual(status, module.CRITICAL)


if __name__ == "__main__":
    unittest.main()

