import re

with open('app/routes/inspector.py', 'r') as f:
    content = f.read()

target = """    except Exception as e:
        return jsonify({"reply": "Intent is unavailable right now — showing raw result only"}), 200"""

replacement = """    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        return jsonify({"reply": f"Intent error: {str(e)}<br><br>{err_msg.replace(chr(10), '<br>')} "}), 200"""

content = content.replace(target, replacement)
with open('app/routes/inspector.py', 'w') as f:
    f.write(content)
