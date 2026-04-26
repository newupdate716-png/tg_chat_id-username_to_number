import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# API Endpoints
TG_INFO_API = "https://tginfo-production-1326.up.railway.app/"
OSINT_API_BASE = "https://abhigyan-codes-tg-to-number-api.onrender.com/@abhigyan_codes/userid="

def process_input(user_input):
    """
    ইনপুট প্রসেসিং লজিক:
    - যদি ইনপুটটি পুরোপুরি সংখ্যা হয় (Chat ID), তবে কোনো @ ছাড়াই সরাসরি যাবে।
    - যদি ইনপুটটি সংখ্যা না হয় (Username), তবে অবশ্যই আগে একটি @ যুক্ত হয়ে যাবে।
    """
    cleaned = user_input.strip()
    
    # যদি ইনপুটে @ থাকে এবং তারপর সংখ্যা থাকে (যেমন @6462069341), তবে @ সরিয়ে দিবে
    if cleaned.startswith('@') and cleaned[1:].isdigit():
        return cleaned[1:]
    
    # যদি ইনপুটটি শুধু সংখ্যা হয়
    if cleaned.isdigit():
        return cleaned
    
    # যদি ইনপুটটি ইউজারনেম হয় (এবং আগে @ না থাকে)
    if not cleaned.startswith('@'):
        return f"@{cleaned}"
        
    return cleaned

@app.route('/lookup', methods=['GET'])
def premium_lookup():
    raw_input = request.args.get('user')
    
    if not raw_input:
        return jsonify({
            "success": False,
            "status": "Error",
            "message": "Username or ID is required to fetch data."
        }), 400

    # প্রসেসড ইনপুট (আইডি হলে শুধু আইডি, ইউজারনেম হলে @সহ)
    target = process_input(raw_input)

    try:
        # --- Step 1: Telegram Information Fetch ---
        tg_res = requests.get(f"{TG_INFO_API}?user={target}", timeout=15)
        tg_data = tg_res.json()

        if not tg_data.get("success"):
            return jsonify({
                "success": False,
                "status": "Data Not Found",
                "message": "Specified user/id does not exist in our database.",
                "error_log": tg_data
            }), 404

        extracted_id = tg_data.get("id")

        # --- Step 2: Intelligence & Number Fetch ---
        osint_res = requests.get(f"{OSINT_API_BASE}{extracted_id}", timeout=15)
        osint_data = osint_res.json() if osint_res.status_code == 200 else {}
        osint_result = osint_data.get("result", {})

        # --- Step 3: Ultra Premium JSON Response Construction ---
        premium_response = {
            "success": True,
            "meta": {
                "status": "200_OK",
                "developer": "SB-SAKIB",
                "engine": "Premium Hybrid API v3.0"
            },
            "profile": {
                "user_id": tg_data.get("id"),
                "username": f"@{tg_data.get('username')}" if tg_data.get("username") else None,
                "first_name": tg_data.get("first_name", "N/A"),
                "last_name": tg_data.get("last_name", "N/A"),
                "full_bio": tg_data.get("bio", "No bio provided"),
                "is_premium": tg_data.get("premium_user", False),
                "profile_image": tg_data.get("public_view", {}).get("web_image")
            },
            "contact_intel": {
                "phone_number": osint_result.get("number", "Private/N/A"),
                "country": osint_result.get("country", "Unknown"),
                "country_code": osint_result.get("country_code", "N/A"),
                "source": osint_result.get("api_used", "Deep-OSINT"),
                "timestamp": osint_result.get("timestamp")
            },
            "security_analysis": {
                "bot_status": tg_data.get("is_bot", False),
                "scam_alert": tg_data.get("is_scam", False),
                "verified": tg_data.get("is_verified", False),
                "leak_report": tg_data.get("leaked_info", "Clean")
            },
            "links": {
                "telegram_url": tg_data.get("public_view", {}).get("telegram_link"),
                "api_support": "https://t.me/sakib01994"
            }
        }

        return jsonify(premium_response), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "status": "System Failure",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=False)
