import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# API Endpoints
TG_INFO_API = "https://tginfo-production-1326.up.railway.app/"
OSINT_API_BASE = "https://abhigyan-codes-tg-to-number-api.onrender.com/@abhigyan_codes/userid="

def format_target(target):
    """
    লজিক: 
    - যদি শুধু সংখ্যা হয় (Chat ID), তবে সরাসরি সংখ্যা রিটার্ন করবে।
    - যদি ইউজারনেম হয় এবং @ না থাকে, তবে @ যোগ করে দিবে।
    - যদি আইডি'র সাথে ভুল করে @ দেয় (যেমন @6462069341), তবে @ সরিয়ে দিবে।
    """
    target = target.strip()
    
    # যদি ইনপুটটি সংখ্যা হয় (Chat ID)
    if target.isdigit():
        return target
    
    # যদি ইনপুটে @ থাকে এবং তারপর সংখ্যা থাকে (যেমন @6462069341)
    if target.startswith('@') and target[1:].isdigit():
        return target[1:]
    
    # যদি সাধারণ ইউজারনেম হয় কিন্তু @ না থাকে
    if not target.startswith('@') and not target.isdigit():
        return f"@{target}"
        
    return target

@app.route('/lookup', methods=['GET'])
def premium_lookup():
    user_input = request.args.get('user')
    
    if not user_input:
        return jsonify({
            "success": False,
            "status": "Missing Parameter",
            "message": "Please provide a Username or Chat ID."
        }), 400

    # ইনপুট ফরম্যাট ঠিক করা
    target = format_target(user_input)

    try:
        # --- Step 1: Telegram Core Info ---
        tg_res = requests.get(f"{TG_INFO_API}?user={target}", timeout=15)
        tg_data = tg_res.json()

        if not tg_data.get("success"):
            return jsonify({
                "success": False,
                "status": "Invalid Entity",
                "message": "User not found. Please check the ID/Username.",
                "debug": tg_data
            }), 404

        # মেইন ডাটা এক্সট্রাক্ট করা
        extracted_id = tg_data.get("id")

        # --- Step 2: OSINT Number Lookup ---
        osint_res = requests.get(f"{OSINT_API_BASE}{extracted_id}", timeout=15)
        osint_data = osint_res.json() if osint_res.status_code == 200 else {}
        osint_result = osint_data.get("result", {})

        # --- Step 3: Ultra Premium JSON Format ---
        premium_output = {
            "success": True,
            "status": "Premium Success",
            "auth_by": "SB-SAKIB",
            "account_details": {
                "user_id": tg_data.get("id"),
                "username": f"@{tg_data.get('username')}" if tg_data.get("username") else "N/A",
                "display_name": f"{tg_data.get('first_name', '')} {tg_data.get('last_name', '')}".strip() or "N/A",
                "biography": tg_data.get("bio", "No bio available"),
                "is_premium": tg_data.get("premium_user", False),
                "avatar_url": tg_data.get("public_view", {}).get("web_image", "N/A")
            },
            "intel_data": {
                "linked_number": osint_result.get("number", "Encrypted/Private"),
                "location_country": osint_result.get("country", "Unknown"),
                "country_iso": osint_result.get("country_code", "N/A"),
                "database_source": osint_result.get("api_used", "OpenOSINT"),
                "lookup_time": osint_result.get("timestamp")
            },
            "security_report": {
                "bot_status": tg_data.get("is_bot", False),
                "scam_alert": tg_data.get("is_scam", False),
                "fake_flag": tg_data.get("is_fake", False),
                "verified_badge": tg_data.get("is_verified", False),
                "leak_history": tg_data.get("leaked_info", "No leak found")
            },
            "platform_links": {
                "profile_link": tg_data.get("public_view", {}).get("telegram_link"),
                "developer_contact": "https://t.me/sakib01994"
            }
        }

        return jsonify(premium_output), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "status": "Server Error",
            "message": "Failed to process request.",
            "error_log": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=False)
