import base64

document = "By clicking agree, you grant the company full rights to share your data with third-party partners. Additionally, you waive all rights to a jury trial and agree to mandatory binding arbitration."

try:
    decoded = base64.b64decode(document)
    text = decoded.decode('utf-8', errors='ignore')
    print("Decoded as base64 garbage:", repr(text))
except Exception as e:
    print("Exception:", e)
