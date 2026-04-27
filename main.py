import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# API Endpoints
TG_INFO_API = "https://tginfo-production-1326.up.railway.app/"
OSINT_API_BASE = "https://abhigyan-codes-tg-to-number-api.onrender.com/@abhigyan_codes/userid="

def clean_target(target):
    """ইউজারনেম বা আইডি থেকে @ চিহ্ন রিমুভ করার লজিক"""
    if target and target.startswith('@'):
        return target[1:]  # @ চিহ্নটি বাদ দিয়ে বাকি অংশ রিটার্ন করবে
    return target

@app.route('/lookup', methods=['GET'])
def premium_lookup():
    raw_target = request.args.get('user')
    
    if not raw_target:
        return jsonify({
            "success": False,
            "status": "Bad Request",
            "message": "Username or Chat ID is required."
        }), 400

    # ইনপুট ক্লিন করা (যেমন: @sbsakib -> sbsakib অথবা @6462069341 -> 6462069341)
    target = clean_target(raw_target)

    try:
        # --- Step 1: Telegram Core Info ---
        tg_res = requests.get(f"{TG_INFO_API}?user={target}", timeout=15)
        tg_data = tg_res.json()

        if not tg_data.get("success"):
            return jsonify({
                "success": False,
                "status": "Not Found",
                "message": "No data found for this entity.",
                "api_response": tg_data
            }), 404

        extracted_id = tg_data.get("id")

        # --- Step 2: OSINT & Number Lookup ---
        osint_res = requests.get(f"{OSINT_API_BASE}{extracted_id}", timeout=15)
        osint_data = osint_res.json() if osint_res.status_code == 200 else {}
        osint_result = osint_data.get("result", {})

        # --- Step 3: Ultra Premium Response Construction ---
        premium_response = {
            "success": True,
            "developer_credit": "SB-SAKIB",
            "execution_status": "Success",
            "data": {
                "profile_summary": {
                    "uid": tg_data.get("id"),
                    "username": f"@{tg_data.get('username')}" if tg_data.get("username") else "N/A",
                    "full_name": f"{tg_data.get('first_name', '')} {tg_data.get('last_name', '')}".strip() or "N/A",
                    "bio": tg_data.get("bio", "No bio available"),
                    "is_premium_account": tg_data.get("premium_user", False),
                    "profile_picture": tg_data.get("public_view", {}).get("web_image", "No Image")
                },
                "contact_intelligence": {
                    "phone_discovery": osint_result.get("number", "Private/Encrypted"),
                    "region": osint_result.get("country", "Global"),
                    "dial_code": osint_result.get("country_code", "N/A"),
                    "provider_source": osint_result.get("api_used", "OpenOSINT"),
                    "fetch_timestamp": osint_result.get("timestamp")
                },
                "security_trust_score": {
                    "is_bot": tg_data.get("is_bot", False),
                    "is_scam": tg_data.get("is_scam", False),
                    "is_fake": tg_data.get("is_fake", False),
                    "is_verified": tg_data.get("is_verified", False),
                    "data_leak_status": tg_data.get("leaked_info", "Clean")
                }
            },
            "system_links": {
                "direct_telegram": tg_data.get("public_view", {}).get("telegram_link"),
                "support_dev": "https://t.me/sakib01994"
            }
        }

        return jsonify(premium_response), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "status": "Internal Error",
            "message": "An unexpected error occurred during processing.",
            "debug": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=False)
