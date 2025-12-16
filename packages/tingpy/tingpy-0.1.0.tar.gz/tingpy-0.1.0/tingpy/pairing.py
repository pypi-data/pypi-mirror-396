import json
import segno
import qrcode


def get_pairing_data(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Extract values from google-services.json structure
    project_id = data['project_info']['project_id']
    messaging_sender_id = data['project_info']['project_number'] # This is the Sender ID
    app_id = data['client'][0]['client_info']['mobilesdk_app_id']
    api_key = data['client'][0]['api_key'][0]['current_key']

    # Return with the EXACT keys the Flutter app expects
    return {
        'projectId': project_id,
        'messagingSenderId': messaging_sender_id,
        'appId': app_id,
        'apiKey': api_key
    }


def print_pairing_qr(json_path):
    minimal_json = get_pairing_data(json_path)
    qr_data = json.dumps(minimal_json)
    qr = segno.make(qr_data)
    print("QR Code for mobile app pairing:")
    # Use qrcode for ASCII terminal display that works in cmd
    ascii_qr = qrcode.QRCode(version=None, box_size=1, border=1)
    ascii_qr.add_data(qr_data)
    ascii_qr.make(fit=True)
    ascii_qr.print_ascii()
    # Also save as PNG for better visibility
    qr.save('pairing_qr.png', scale=4)
    print("QR code also saved as 'pairing_qr.png' - you can open this image file to scan")
