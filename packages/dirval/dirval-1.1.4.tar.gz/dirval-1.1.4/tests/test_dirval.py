import os
import json
import shutil
import tempfile
import unittest

from dirval.core import (
    generate_directory_hash,
    create_stamp_file,
    validate,
    STAMP_FILENAME,
)


class TestDirectoryValidator(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="dirval_test_")
        os.makedirs(os.path.join(self.tmpdir, "subdir"), exist_ok=True)
        with open(os.path.join(self.tmpdir, "a.txt"), "w") as f:
            f.write("hello\n")
        with open(os.path.join(self.tmpdir, "subdir", "b.txt"), "w") as f:
            f.write("world\n")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_generate_hash_consistency(self):
        h1 = generate_directory_hash(self.tmpdir)
        h2 = generate_directory_hash(self.tmpdir)
        self.assertIsInstance(h1, str)
        self.assertEqual(h1, h2, "Hash should be deterministic for unchanged directories")

    def test_generate_hash_nonexistent_dir(self):
        missing = os.path.join(self.tmpdir, "does_not_exist")
        h = generate_directory_hash(missing)
        self.assertEqual(h, -1)

    def test_stamp_creation_and_successful_validation(self):
        create_stamp_file(self.tmpdir)

        stamp_path = os.path.join(self.tmpdir, STAMP_FILENAME)
        self.assertTrue(os.path.exists(stamp_path))

        with open(stamp_path, "r") as f:
            data = json.load(f)
        self.assertIn("hash", data)
        self.assertIn("date", data)

        with self.assertRaises(SystemExit) as cm:
            validate(self.tmpdir)
        self.assertEqual(cm.exception.code, 0)

    def test_validation_fails_when_changed(self):
        create_stamp_file(self.tmpdir)

        with open(os.path.join(self.tmpdir, "new_file.txt"), "w") as f:
            f.write("change\n")

        with self.assertRaises(SystemExit) as cm:
            validate(self.tmpdir)
        self.assertEqual(cm.exception.code, 1, "Validation should fail after changes")

    def test_stamp_exists_exits_with_code_2(self):
        create_stamp_file(self.tmpdir)
        with self.assertRaises(SystemExit) as cm:
            create_stamp_file(self.tmpdir)
        self.assertEqual(cm.exception.code, 2)

    def test_missing_stamp_exits_with_code_3(self):
        with self.assertRaises(SystemExit) as cm:
            validate(self.tmpdir)
        self.assertEqual(cm.exception.code, 3)

    def test_hash_ignores_stamp_file(self):
        before = generate_directory_hash(self.tmpdir)
        create_stamp_file(self.tmpdir)
        after = generate_directory_hash(self.tmpdir)
        self.assertEqual(before, after, "Hash must not change after creating the stamp file")

    def test_stamp_nonexistent_directory_exits_with_code_3(self):
        missing = os.path.join(self.tmpdir, "does_not_exist")
        with self.assertRaises(SystemExit) as cm:
            create_stamp_file(missing)
        self.assertEqual(cm.exception.code, 3)

    def test_stamp_path_is_file_exits_with_code_3(self):
        file_path = os.path.join(self.tmpdir, "somefile.txt")
        with open(file_path, "w") as f:
            f.write("not a directory\n")

        with self.assertRaises(SystemExit) as cm:
            create_stamp_file(file_path)
        self.assertEqual(cm.exception.code, 3)

    def test_validate_nonexistent_directory_exits_with_code_3(self):
        missing = os.path.join(self.tmpdir, "does_not_exist")
        with self.assertRaises(SystemExit) as cm:
            validate(missing)
        self.assertEqual(cm.exception.code, 3)

    def test_validate_path_is_file_exits_with_code_3(self):
        file_path = os.path.join(self.tmpdir, "somefile.txt")
        with open(file_path, "w") as f:
            f.write("not a directory\n")

        with self.assertRaises(SystemExit) as cm:
            validate(file_path)
        self.assertEqual(cm.exception.code, 3)
