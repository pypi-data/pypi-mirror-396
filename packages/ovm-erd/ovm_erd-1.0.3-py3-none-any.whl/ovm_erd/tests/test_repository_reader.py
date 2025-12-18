import unittest
import os
from ovm_erd.repository_reader import (
    get_repository_path,
    read_repository,
    build_metadata_dict,
    save_to_textfile
)

class TestRepositoryReader(unittest.TestCase):

    def test_get_repository_path_fallback(self):
        # Simuleer een lege of ongeldig pad door global overschrijven
        path = get_repository_path()
        self.assertTrue(isinstance(path, str))
        self.assertTrue(os.path.exists(path) or path == example_path)

    def test_read_repository_output(self):
        # Test of er een dict terugkomt, ook als deze leeg is
        path = get_repository_path()
        result = read_repository(path)
        self.assertIsInstance(result, dict)

    def test_build_metadata_structure(self):
        # Dummy-bestand met tags, pk, fk, hashdiff, etc.
        dummy_files = {
            "example.sql": {
                "content": '''
                    set source_model = "dummy"
                    set src_pk = "id"
                    set src_fk = ["region_id"]
                    set src_hashdiff = "hash_id"
                    set src_eff = "valid_from"
                    set src_nk = "natural_key"
                    tags = ["core", "hub"]
                '''
            }
        }

        metadata = build_metadata_dict(dummy_files)
        self.assertIsInstance(metadata, dict)
        self.assertIn("example.sql", metadata)

        m = metadata["example.sql"]
        self.assertEqual(m["table_name"], "example")
        self.assertEqual(m["pk"], "id")
        self.assertEqual(m["fk"], ["region_id"])
        self.assertEqual(m["hashdiff"], "hash_id")
        self.assertEqual(m["src_effective_date"], "valid_from")
        self.assertEqual(m["nk"], "natural_key")
        self.assertEqual(m["pattern"], "hub")
        self.assertIn("core", m["tags"])
        self.assertIn("hub", m["tags"])


if __name__ == "__main__":
    unittest.main()
