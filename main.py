import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# API Endpoints
TG_INFO_API = "https://tginfo-production-1326.up.railway.app/"
OSINT_API_BASE = "https://abhigyan-codes-tg-to-number-api.onrender.com/@abhigyan_codes/userid="

@app.route('/lookup', methods=['GET'])
def premium_lookup():
    # ইউজার এখানে @username অথবা numeric id যেকোনো একটি দিতে পারবে
    target = request.args.get('user')
    
    if not target:
        return jsonify({
            "success": False,
            "message": "Please provide a username or Chat ID (e.g., ?user=@sakib01994 or ?user=5556909453)"
        }), 400

    try:
        # Step 1: Fetch Data from the first API (Supports both ID and Username)
        # এই এপিআইটি আইডি বা ইউজারনেম দুইটাই এক্সেপ্ট করে
        tg_res = requests.get(f"{TG_INFO_API}?user={target}", timeout=15)
        tg_data = tg_res.json()

        if not tg_data.get("success"):
            return jsonify({
                "success": False,
                "message": "User not found in Telegram database",
                "error_details": tg_data
            }), 404

        # এখান থেকে অরিজিনাল নিউমেরিক আইডি নেওয়া হচ্ছে
        extracted_id = tg_data.get("id")

        # Step 2: Fetch OSINT/Number Info using the extracted numeric ID
        osint_res = requests.get(f"{OSINT_API_BASE}{extracted_id}", timeout=15)
        osint_data = osint_res.json()

        # Step 3: Premium Combined JSON Formatting
        result = {
            "success": True,
            "status": "Ultra Premium Fetch",
            "developer": "SB-SAKIB",
            "user_info": {
                "id": tg_data.get("id"),
                "username": tg_data.get("username"),
                "first_name": tg_data.get("first_name"),
                "last_name": tg_data.get("last_name"),
                "bio": tg_data.get("bio"),
                "premium_status": tg_data.get("premium_user"),
                "profile_picture": tg_data.get("public_view", {}).get("web_image")
            },
            "security_info": {
                "is_bot": tg_data.get("is_bot"),
                "is_scam": tg_data.get("is_scam"),
                "is_fake": tg_data.get("is_fake"),
                "verified": tg_data.get("is_verified"),
                "leaked_data": tg_data.get("leaked_info")
            },
            "network_info": {
                "phone_number": osint_data.get("result", {}).get("number", "Private/Hidden"),
                "country": osint_data.get("result", {}).get("country", "Unknown"),
                "country_code": osint_data.get("result", {}).get("country_code"),
                "provider_info": osint_data.get("result", {}).get("api_used"),
                "response_timestamp": osint_data.get("result", {}).get("timestamp")
            }
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "status": "Server Error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=False)