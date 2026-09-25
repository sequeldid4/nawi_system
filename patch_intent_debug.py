with open('app/routes/inspector.py', 'r') as f:
    content = f.read()

target = "const errText = \"Intent is unavailable right now.\";"
# We want to change the backend to send the error message!
backend_target = """        except Exception as e:
        return jsonify({"reply": "Intent is unavailable right now — showing raw result only"}), 200"""
backend_replacement = """        except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        return jsonify({"reply": f"Intent error: {str(e)} - {err_msg}"}), 500"""

content = content.replace(backend_target, backend_replacement)
with open('app/routes/inspector.py', 'w') as f:
    f.write(content)
