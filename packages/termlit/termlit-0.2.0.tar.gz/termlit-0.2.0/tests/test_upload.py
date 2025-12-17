import tempfile
import unittest
from pathlib import Path

from termlit import session as session_mod


class DummySession:
    def __init__(self):
        self.messages: list[str] = []
        self.username = "tester"

    def send(self, message: str = "", newline: bool = True) -> None:
        self.messages.append(message)


class UploadFileReplaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.session = DummySession()
        session_mod.bind_session(self.session)

    def tearDown(self) -> None:
        session_mod.unbind_session()
        self._tmp.cleanup()

    def test_replace_same_path_skips_copy(self) -> None:
        source = self.base / "report.txt"
        source.write_text("payload")

        result = session_mod.upload_file(
            source,
            destination_dir=self.base,
            replace=True,
            show_progress=True,
        )

        self.assertEqual(result, source)
        self.assertEqual(source.read_text(), "payload")
        self.assertTrue(
            any("skipped self-copy" in msg for msg in self.session.messages),
            msg=self.session.messages,
        )
