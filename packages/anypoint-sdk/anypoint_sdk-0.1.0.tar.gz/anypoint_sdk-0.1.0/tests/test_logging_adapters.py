# tests/test_logging_adapters.py
import logging
import unittest

from anypoint_sdk._logging import NullLogger, StdlibLogger, default_logger


class _Capture(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


class LoggingAdaptersTests(unittest.TestCase):
    def test_default_logger_installs_single_nullhandler(self):
        base = logging.getLogger("anypoint_sdk")

        def count_nh() -> int:
            return sum(1 for h in base.handlers if isinstance(h, logging.NullHandler))

        l1 = default_logger()
        after_first = count_nh()
        l2 = default_logger()
        after_second = count_nh()

        self.assertIsInstance(l1, StdlibLogger)
        self.assertIsInstance(l2, StdlibLogger)

        # At least one NullHandler installed, and calling again does not add more
        self.assertGreaterEqual(after_first, 1)
        self.assertEqual(after_second, after_first)

    def test_stdliblogger_delegates_and_child_names_logger(self):
        # Isolated stdlib logger
        base = logging.getLogger("anypoint_sdk.testcase")
        base.propagate = False
        base.setLevel(logging.DEBUG)  # <— make INFO/DEBUG visible

        cap = _Capture()
        cap.setLevel(logging.DEBUG)  # <— capture all levels
        base.addHandler(cap)
        try:
            log = StdlibLogger(base)
            log.debug("dbg %s", "x")  # emitted by base
            log.info("info")
            log.warning("warn")
            log.error("err")

            child = log.child("sub")
            child.info("child-info")  # emitted by child, propagates to base

            names = [rec.name for rec in cap.records]
            msgs = [rec.getMessage() for rec in cap.records]

            # Child record keeps its own logger name
            self.assertIn("anypoint_sdk.testcase.sub", names)
            self.assertIn("anypoint_sdk.testcase", names)
            self.assertIn("dbg x", msgs)
            self.assertIn("child-info", msgs)
        finally:
            base.removeHandler(cap)  # cleanup to avoid cross-test leakage

    def test_nulllogger_is_noop_and_child_returns_self(self):
        log = NullLogger()
        # Should not raise
        log.debug("a")
        log.info("b")
        log.warning("c")
        log.error("d")
        # Child is the same instance
        self.assertIs(log.child("anything"), log)


if __name__ == "__main__":
    unittest.main()
