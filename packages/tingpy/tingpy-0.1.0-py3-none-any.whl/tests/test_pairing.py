import unittest
import tempfile
import json
from tingpy.pairing import get_pairing_data


class TestPairing(unittest.TestCase):
    def test_get_pairing_data(self):
        sample_data = {
            "project_info": {
                "project_id": "my-test-project",
                "project_number": "123456789"
            },
            "client": [
                {
                    "client_info": {
                        "mobilesdk_app_id": "1:123456789:android:abcdef123456"
                    },
                    "api_key": [
                        {
                            "current_key": "AIzaSyAbCdEfGhIjKlMnOpQrStUvWxYz"
                        }
                    ]
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_data, f)
            f.flush()
            result = get_pairing_data(f.name)

        expected = {
            'project_id': 'my-test-project',
            'project_number': '123456789',
            'app_id': '1:123456789:android:abcdef123456',
            'api_key': 'AIzaSyAbCdEfGhIjKlMnOpQrStUvWxYz'
        }

        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
